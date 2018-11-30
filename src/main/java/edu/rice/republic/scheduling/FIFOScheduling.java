package edu.rice.republic.scheduling;

import edu.rice.bold.network.P2MPwR;
import edu.rice.republic.common.RequestState;
import edu.rice.republic.common.Schedule;
import edu.rice.republic.event.AEvent;
import edu.rice.republic.event.FinishEvent;
import edu.rice.republic.event.RequestEvent;
import org.apache.log4j.Logger;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

/**
 * Created by xs6 on 3/27/18.
 */
public class FIFOScheduling extends AScheduling {
    private final static Logger logger = Logger.getLogger(FIFOScheduling.class.getName());
    private static FIFOScheduling ourInstance = new FIFOScheduling();

    public static FIFOScheduling getInstance() {
        return ourInstance;
    }

    private FIFOScheduling() {
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
            logger.info("number of active requests:\t" + rqstates.size());

            for (RequestState rqstate : rqstates) {
                if (rsmgmt.validResource(rqstate.rq)) {
                    rsmgmt.reserveResource(rqstate.rq);
                    Schedule sched = new Schedule(rqstate.rq, rqstate.rq.datasize);
                    logger.info("new schedule:\t" + sched);
                    rqmgmt.scheduleRequest(sched);
                } else {
                    break;
                }
            }
        }
    }
}
