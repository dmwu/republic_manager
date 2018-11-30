package edu.rice.republic.resourcemgmt;

import edu.rice.republic.amif.Request;
import edu.rice.republic.common.Resource;
import edu.rice.republic.scheduling.AScheduling;
import org.apache.log4j.Logger;

import java.util.Arrays;
import java.util.List;

/**
 * Created by xs6 on 3/26/18.
 */
public class ResourceManager implements IResourceManager {
    private final static Logger logger = Logger.getLogger(ResourceManager.class.getName());
    public AScheduling scheduling;
    private boolean[] validity_sender = new boolean[40];
    private boolean[] validity_receiver = new boolean[40];

    private static ResourceManager ourInstance = new ResourceManager();

    public static ResourceManager getInstance() {
        return ourInstance;
    }

    private ResourceManager() {
        Arrays.fill(validity_sender, true);
        Arrays.fill(validity_receiver, true);
    }

    @Override
    public Resource getResource() {
        return null;
    }

    @Override
    public boolean validResources(List<Request> rqs) {
        return false;
    }

    @Override
    public boolean validResource(Request rq) {
        if (!validity_sender[Integer.valueOf(rq.sender.split("\\.")[3]) - 111]) {
            logger.info("sender:\t" + rq.sender + " is not valid");
            return false;
        }
        for (String receiver : rq.receivers) {
            if (!validity_receiver[Integer.valueOf(receiver.split("\\.")[3]) - 111]) {
                logger.info("receiver:\t" + receiver + " is not valid");
                return false;
            }
        }
        return true;
    }

    @Override
    public void reserveResources(List<Request> rqs) {

    }

    @Override
    public void reserveResource(Request rq) {

        validity_sender[Integer.valueOf(rq.sender.split("\\.")[3]) - 111] = false;
        logger.info("sender:\t" + rq.sender + " is reserved");
        for (String receiver : rq.receivers) {
            logger.info("receiver:\t" + receiver + " is reserved");
            validity_receiver[Integer.valueOf(receiver.split("\\.")[3]) - 111] = false;
        }
    }

    @Override
    public void returnResource(Request rq) {
        validity_sender[Integer.valueOf(rq.sender.split("\\.")[3]) - 111] = true;
        logger.info("sender:\t" + rq.sender + " is freed");
        for (String receiver : rq.receivers) {
            logger.info("receiver:\t" + receiver + " is freed");
            validity_receiver[Integer.valueOf(receiver.split("\\.")[3]) - 111] = true;
        }
    }
}
