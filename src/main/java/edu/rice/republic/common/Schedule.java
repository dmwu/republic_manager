package edu.rice.republic.common;

import edu.rice.republic.amif.Request;
import edu.rice.republic.amif.Response;

/**
 * Created by xs6 on 3/26/18.
 */
public class Schedule {
    public Request rq;

    public long schedsize;

    public SchedState state;

    public Schedule(Request rq, long size) {
        this.rq = rq;
        this.schedsize = size;
        this.state = SchedState.SCHEDULED;
    }

    public void finished() {
        assert (state == SchedState.SCHEDULED);
        state = SchedState.FINISHED;
    }


    enum SchedState {
        SCHEDULED, FINISHED
    }
}
