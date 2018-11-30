package edu.rice.republic.scheduling;

import edu.rice.republic.common.RequestState;
import edu.rice.republic.common.Schedule;
import edu.rice.republic.event.AEvent;
import edu.rice.republic.event.FinishEvent;
import edu.rice.republic.event.RequestEvent;
import org.apache.log4j.Logger;

import java.util.Comparator;
import java.util.List;
import java.util.concurrent.LinkedBlockingQueue;

/**
 * Created by xs6 on 4/5/18.
 */
public class FixedQuantumFIFOSchedulling extends AScheduling {
    private final static Logger logger = Logger.getLogger(FixedQuantumFIFOSchedulling.class.getName());
    private static FixedQuantumFIFOSchedulling ourInstance = new FixedQuantumFIFOSchedulling();

    public static FixedQuantumFIFOSchedulling getInstance() {
        return ourInstance;
    }

    private FixedQuantumFIFOSchedulling() {
        eventqueue = new LinkedBlockingQueue<>();
    }

    @Override
    public void run() {
        logger.info("thread started");
        while (true) {
            AEvent event = null;
            try {
                event = this.eventqueue.take();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            logger.info("receive an event:\t" + event);

            if (!(event instanceof RequestEvent) && !(event instanceof FinishEvent)) {
                continue;
            }

            // collect all active requests (requests that have not been completely scheduled)
            List<RequestState> rqstates = rqmgmt.getRequests();
            rqstates.sort(new Comparator<RequestState>() {
                @Override
                public int compare(RequestState o1, RequestState o2) {
                    return o1.ts.compareTo(o2.ts);
                }
            });
            logger.info("number of active requests:\t" + rqstates.size());
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            for (RequestState rqstate : rqstates) {
                if (rsmgmt.validResource(rqstate.rq)) {
                    rsmgmt.reserveResource(rqstate.rq);
                    Schedule sched = new Schedule(rqstate.rq, rqstate.rq.remainingsize >= 100 ? 100 : rqstate.rq.remainingsize);
                    logger.info("new schedule:\t" + sched);
                    rqmgmt.scheduleRequest(sched);
                } else {
                    break;
                }
            }
        }
    }
}
