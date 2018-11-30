package edu.rice.bold.network;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;

/**
 * Created by xs6 on 8/23/16.
 */
public class Resource {
    final private Server upServer;
    final private HashSet<Server> downServers;
    final private Link upLink;
    final private HashSet<Link> downLinks;
    final private P2MPwR p2mpwr;
    final private boolean useOptical;
    private ArrayList<String> ocsCmd;
    private Map<Integer, ArrayList<String>> torCmd;

    public Resource(Server upServer, HashSet<Server> downServers, Link upLink, HashSet<Link> downLinks, P2MPwR p2mpwr) {
        this.upServer = upServer;
        this.downServers = downServers;
        this.upLink = upLink;
        this.downLinks = downLinks;
        this.p2mpwr = p2mpwr;
        this.useOptical = true;
    }

    public Resource(Server upServer, HashSet<Server> downServers) {
        this.upServer = upServer;
        this.downServers = downServers;
        this.upLink = null;
        this.downLinks = null;
        this.p2mpwr = null;
        this.useOptical = false;
    }

    public boolean isFeasible() {
        if (!upServer.isUpValid()) {
            System.out.println("[warn][upServer]" + upServer + " is not valid up");
            return false;
        }
        for (Server s : downServers) {
            if (!s.isDownValid()) {
                System.out.println("[warn][downServer]" + s + " is not valid");
                return false;
            }
        }
        if (useOptical) {
            if (!upLink.isUpValid()) {
                System.out.println("[warn][upLink]" + upLink + " is not valid [up]");
                return false;
            }
            if (!upLink.isDownValid()) {
                System.out.println("[warn][upLink]" + upLink + " is not valid [down]");
                return false;
            }
            for (Link dl : downLinks) {
                if (!dl.isDownValid()) {
                    System.out.println("[warn][downLink]" + dl + " is not valid");
                    return false;
                }
            }
            if (p2mpwr != null) {
                if (p2mpwr.getSplitters() != null) { // splitter is required
                    for (AComponent sp : p2mpwr.getSplitters()) {
                        assert (sp.isValid());
                    }
                } else {
                    System.out.println("[warn][splitter] no valid splitters");
                    return false;
                }
                if (p2mpwr.getRelays() != null) { // relay is optinal
                    for (AComponent rly : p2mpwr.getRelays()) {
                        assert (rly.isValid());
                    }
                }
                if (p2mpwr.getFeeder() != null) { // feeder is required
                    assert (p2mpwr.getFeeder().isValid());
                } else {
                    System.out.println("[warn][feeder] no valid feeder");
                    return false;
                }
            } else {
                System.out.println("[warn][p2mpwr] no valid p2mpwr");
                return false;
            }
        }
        return true;
    }

    public void acquire(Map<InOuts, P2MPwR> iosP2MPMap) {
        upServer.acquireUpServer();
        for (Server ds : downServers) {
            ds.acquireDownServer();
        }
        if (useOptical) {
            upLink.acquireUpLink(upLink, downLinks, iosP2MPMap);
            upLink.acquireDownLink(upLink, downLinks, iosP2MPMap);
            for (Link dl : downLinks) {
                dl.acquireDownLink(upLink, downLinks, iosP2MPMap);
            }

            for (AComponent sp : p2mpwr.getSplitters()) {
                sp.reserve(upLink, downLinks, iosP2MPMap);
            }
            if (p2mpwr.getRelays() != null) {
                for (AComponent rly : p2mpwr.getRelays()) {
                    rly.reserve(upLink, downLinks, iosP2MPMap);
                }
            }
            p2mpwr.getFeeder().reserve(upLink, downLinks, iosP2MPMap);
        }
    }

    public void release() {
        upServer.releaseUpServer();
        for (Server s : downServers) {
            s.releaseDownServer();
        }
        if (useOptical) {
            upLink.releaseUpLink();
            upLink.releaseDownLink();
            for (Link dl : downLinks) {
                dl.releaseDownLink();
            }

            for (AComponent sp : p2mpwr.getSplitters()) {
                sp.release();
            }
            if (p2mpwr.getRelays() != null) {
                for (AComponent rly : p2mpwr.getRelays()) {
                    rly.release();
                }
            }
            p2mpwr.getFeeder().release();
        }
    }

    @Override
    public String toString() {
        return "Resource{" +
                "upServer=" + upServer +
                ", downServers=" + downServers +
                ", upLink=" + upLink +
                ", downLinks=" + downLinks +
                ", p2mpwr=" + p2mpwr +
                ", useOptical=" + useOptical +
                '}';
    }

    public ArrayList<String> getOcsCmd() {
        return ocsCmd;
    }

    public void setOcsCmd(ArrayList<String> ocsCmd) {
        this.ocsCmd = ocsCmd;
    }

    public Map<Integer, ArrayList<String>> getTorCmd() {
        return torCmd;
    }

    public void setTorCmd(Map<Integer, ArrayList<String>> torCmd) {
        this.torCmd = torCmd;
    }

    public boolean isUseOptical() {
        return useOptical;
    }
}
