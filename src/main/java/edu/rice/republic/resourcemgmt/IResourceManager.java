package edu.rice.republic.resourcemgmt;

import edu.rice.republic.amif.Release;
import edu.rice.republic.amif.Request;
import edu.rice.republic.common.Resource;
import edu.rice.republic.common.Schedule;

import java.util.List;

/**
 * Created by xs6 on 3/26/18.
 */
public interface IResourceManager {

    Resource getResource();

    boolean validResources(List<Request> rqs);

    boolean validResource(Request rq);

    void reserveResources(List<Request> rqs);

    void reserveResource(Request rqs);

    void returnResource(Request rqs);
}
