package edu.rice.republic.common;

import edu.rice.republic.amif.Request;
import edu.rice.republic.amif.Response;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by xs6 on 3/26/18.
 */
public class RequestState {
    public Request rq;
    public int sched_started; // index to the schedule that has been started
    public int sched_finished; // index to the schedule that has finished
    public long sched_datasize; // bytes for the scheduled
    public List<Schedule> scheds; // all the schedules
    public boolean waiting;
    public Timestamp ts;

    public RequestState(Request rq) {
        this.rq = rq;
        this.scheds = new ArrayList<>();
        sched_started = -1;
        sched_finished = -1;
        sched_datasize = 0;
        waiting = false;
        ts = new Timestamp(System.currentTimeMillis());
    }

    public void schedule(long size) {

    }

    public void finish(int rpid) {
        sched_finished++;
        assert (rpid == sched_finished);
        scheds.get(rpid).finished();
    }
}
