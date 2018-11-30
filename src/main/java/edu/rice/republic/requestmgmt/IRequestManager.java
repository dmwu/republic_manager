package edu.rice.republic.requestmgmt;

import edu.rice.republic.common.RequestState;
import edu.rice.republic.common.Schedule;
import edu.rice.republic.amif.Release;
import edu.rice.republic.amif.Request;

import java.util.List;

/**
 * Created by xs6 on 3/26/18.
 */
public interface IRequestManager {
    RequestState addRequest(Request rq); // called by a-m interface

    List<RequestState> getRequests(); // called by scheduler and stats

    void scheduleRequests(List<Schedule> scheds); // called by scheduler

    void scheduleRequest(Schedule sched); // called by scheduler

    void finishSchedule(Release rl);

}
