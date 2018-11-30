package edu.rice.republic.server;

import edu.rice.republic.amif.*;
import edu.rice.republic.common.RequestState;
import edu.rice.republic.event.AEvent;
import edu.rice.republic.event.FinishEvent;
import edu.rice.republic.event.RequestEvent;
import edu.rice.republic.requestmgmt.RequestManager;
import edu.rice.republic.resourcemgmt.ResourceManager;
import edu.rice.republic.scheduling.AScheduling;
import edu.rice.republic.scheduling.BestEffortScheduling;
import edu.rice.republic.scheduling.FIFOScheduling;
import edu.rice.republic.scheduling.FixedQuantumFIFOSchedulling;
import org.apache.log4j.Logger;
import org.apache.thrift.TException;

/**
 * Created by xs6 on 3/26/18.
 */
public class ManagerImpl implements AgentManagerInterface.Iface {
    private final static Logger logger = Logger.getLogger(ManagerImpl.class.getName());
    RequestManager rqm = RequestManager.getInstance();
    ResourceManager rsm = ResourceManager.getInstance();
    AScheduling scheduling = FixedQuantumFIFOSchedulling.getInstance();

    public ManagerImpl() {
        logger.debug("instance created");
        scheduling.rqmgmt = RequestManager.getInstance();
        scheduling.rsmgmt = ResourceManager.getInstance();
        rqm.scheduling = scheduling;
        rsm.scheduling = scheduling;
        new Thread(this.scheduling).start();
    }

    @Override
    public Response request(Request rq) throws TException {
        logger.info("request received:\t" + rq.toString());

        // update request pool with new request (wrapped in a requeststate)
        RequestState rqstate = rqm.addRequest(rq); // the object that will wait on
        logger.info("request state:\t" + rqstate.toString());

        // trigger the scheduling
        AEvent event = new RequestEvent();
        logger.info("a request event:\t" + event);
        scheduling.eventqueue.offer(event);

        // wait for schedule
        synchronized (rqstate) {
            if (rqstate.sched_started + 1 < rqstate.scheds.size()) {
                logger.info("a new schedule has been generated, no need to wait:\t" + rqstate.sched_started + '/' + rqstate.scheds.size());
            } else {
                try {
                    rqstate.waiting = true;
                    rqstate.wait(); // TODO: what if the wait misses the notify().....
                    rqstate.waiting = false;
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }

        boolean new_schedule = rqstate.sched_started + 1 < rqstate.scheds.size();
        rqstate.sched_started += (new_schedule ? 1 : 0);

        Response rp = new Response(rq.rqid,
                new_schedule ? rqstate.sched_started : -1,
                new_schedule ? ResponseType.ACCEPT : ResponseType.DENY,
                0L,
                new_schedule ? rqstate.scheds.get(rqstate.sched_started).schedsize : 0L
        );

        logger.info("response issued:\t" + rp.toString());
        return rp;
    }

    @Override
    public void release(Release rl) throws TException {
        logger.info("release received:\t" + rl.toString());

        // update request pool with the finishing of the request
        rqm.finishSchedule(rl);

        // notify the path management
        rsm.returnResource(rqm.rqs_map.get(rl.rqid).rq);

        // create the finish event
        AEvent event = new FinishEvent();
        logger.info("a finish event:\t" + event);
        scheduling.eventqueue.offer(event);
    }
}
