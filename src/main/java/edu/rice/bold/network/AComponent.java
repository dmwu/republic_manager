package edu.rice.bold.network;

import java.util.Map;
import java.util.Set;

/**
 * Created by xs6 on 11/22/17.
 */
public abstract class AComponent {
    protected boolean isValid;
    protected ComponentPool cp;
    private InOuts ios;

    public InOuts getIos() {
        return ios;
    }

    public AComponent() {
        isValid = true;

    }

    public void access() {
        cp.access(this);
    }

    public void setValid(boolean valid) {
        isValid = valid;
    }

    public boolean isValid() {
        return isValid;
    }

    public void reserve(Link upLink, Set<Link> downLinks, Map<InOuts, P2MPwR> iosP2MPMap) {
        setValid(false);
        access();
        if (iosP2MPMap.containsKey(ios)) {
            iosP2MPMap.remove(ios);
        }
        ios = new InOuts(upLink, downLinks);
    }

    public void release() {
        setValid(true);
    }

}
