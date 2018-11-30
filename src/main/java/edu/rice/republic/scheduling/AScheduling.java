package edu.rice.republic.scheduling;

import edu.rice.republic.event.AEvent;
import edu.rice.republic.requestmgmt.IRequestManager;
import edu.rice.republic.resourcemgmt.IResourceManager;

import java.util.concurrent.BlockingQueue;

/**
 * Created by xs6 on 3/27/18.
 */
public abstract class AScheduling implements Runnable {
    public BlockingQueue<AEvent> eventqueue;
    public IRequestManager rqmgmt;
    public IResourceManager rsmgmt;
}
