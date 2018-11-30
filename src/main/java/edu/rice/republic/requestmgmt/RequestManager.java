package edu.rice.republic.requestmgmt;

import edu.rice.republic.amif.Release;
import edu.rice.republic.amif.Request;
import edu.rice.republic.common.RequestState;
import edu.rice.republic.common.Schedule;
import edu.rice.republic.event.AEvent;
import edu.rice.republic.event.FinishEvent;
import edu.rice.republic.event.RequestEvent;
import edu.rice.republic.resourcemgmt.ResourceManager;
import edu.rice.republic.scheduling.AScheduling;
import edu.rice.republic.scheduling.FIFOScheduling;
import org.apache.log4j.Logger;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.LinkedBlockingQueue;

/**
 * Created by xs6 on 3/26/18.
 */
public class RequestManager implements IRequestManager {
    private final static Logger logger = Logger.getLogger(RequestManager.class.getName());
    public AScheduling scheduling;
    public Map<String, RequestState> rqs_map = new ConcurrentHashMap<>(); // map RequestID to RequestState

    private static RequestManager ourInstance = new RequestManager();

    public static RequestManager getInstance() {
        return ourInstance;
    }

    private RequestManager() {

    }

    @Override
    public RequestState addRequest(Request rq) {
        RequestState rqstate;
        if (rqs_map.containsKey(rq.rqid)) {
            logger.info("a follow-up request");
            rqstate = rqs_map.get(rq.rqid);
        } else {
            logger.info("a new request");
            rqstate = new RequestState(rq); // TODO: confirm rq is the same as rqstate.rq
            rqs_map.put(rq.rqid, rqstate);
        }
        return rqstate;
    }

    @Override
    public List<RequestState> getRequests() {
        List<RequestState> ret = new ArrayList<>();
        for (RequestState rqstate : rqs_map.values()) {
            if (rqstate.sched_datasize != rqstate.rq.datasize) {
                ret.add(rqstate);
            }
        }
        return ret;
    }

    @Override
    public void scheduleRequests(List<Schedule> scheds) {
        for (Schedule sched : scheds) {
            scheduleRequest(sched);
        }
    }

    @Override
    public void scheduleRequest(Schedule sched) {
        RequestState rqstate = rqs_map.get(sched.rq.rqid);
        synchronized (rqstate) {
            rqstate.scheds.add(sched);
            rqstate.sched_datasize += sched.schedsize;

            // request for the schedule has not been received.
            if (rqstate.waiting) { // request for the schedule is waiting
                rqstate.notify();
            }
        }
    }

    @Override
    public void finishSchedule(Release rl) {
        rqs_map.get(rl.rqid).finish(rl.rpid);
    }
}
