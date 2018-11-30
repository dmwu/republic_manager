package edu.rice.bold.network;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

/**
 * Created by xs6 on 8/15/16.
 */
public class Link {
    final private int torLog;
    final private int torPhy;
    final private int portTor;
    final private int portOcs;
    private boolean upValid;
    private boolean downValid;
    private InOuts upIos;
    private InOuts downIos;

    public Link(int tor_log, int tor_phy, int port_tor, int port_ocs) {
        this(tor_log, tor_phy, port_tor, port_ocs, true);
    }

    public Link(int tor_log, int tor_phy, int port_tor, int port_ocs, boolean valid) {
        this.torLog = tor_log;
        this.torPhy = tor_phy;
        this.portTor = port_tor;
        this.portOcs = port_ocs;
        this.upValid = valid;
        this.downValid = valid;
    }

    public int getTorLog() {
        return torLog;
    }

    public int getTorPhy() {
        return torPhy;
    }

    public int getPortTor() {
        return portTor;
    }

    public int getPortOcs() {
        return portOcs;
    }

    public boolean isUpValid() {
        return upValid;
    }

    public void setUpValid(boolean upValid) {
        this.upValid = upValid;
    }

    public boolean isDownValid() {
        return downValid;
    }

    public void setDownValid(boolean downValid) {
        this.downValid = downValid;
    }

    public void acquireUpLink(Link upLink, Set<Link> downLinks, Map<InOuts, P2MPwR> iosP2MPMap) {
        setUpValid(false);
        if (iosP2MPMap.containsKey(upIos)) {
            iosP2MPMap.remove(upIos);
        }
        upIos = new InOuts(upLink, downLinks);
    }

    public void acquireDownLink(Link upLink, Set<Link> downLinks, Map<InOuts, P2MPwR> iosP2MPMap) {
        setDownValid(false);
        if (iosP2MPMap.containsKey(downIos)) {
            iosP2MPMap.remove(downIos);
        }
        downIos = new InOuts(upLink, downLinks);
    }

    public void releaseUpLink() {
        setUpValid(true);
    }

    public void releaseDownLink() {
        setDownValid(true);
    }

    @Override
    public String toString() {
        return "Link{" +
                "torLog=" + torLog +
                ", torPhy=" + torPhy +
                ", portTor=" + portTor +
                ", portOcs=" + portOcs +
                ", upValid=" + upValid +
                ", downValid=" + downValid +
                '}';
    }

    public static Map<Integer, Link> load(String filename) {
        JSONParser parser = new JSONParser();
        JSONArray jsonList = null;
        try {
            jsonList = (JSONArray) parser.parse(new FileReader(filename));
        } catch (IOException | ParseException e) {
            e.printStackTrace();
        }

        HashMap<Integer, Link> ret = new HashMap<Integer, Link>();
        if (jsonList != null) {
            Iterator<JSONObject> iterator = (Iterator<JSONObject>) jsonList.iterator();
            while (iterator.hasNext()) {
                JSONObject linkObj = iterator.next();

                int tor_log = ((Long) linkObj.get("tor_log")).intValue();
                int tor_phy = ((Long) linkObj.get("tor_phy")).intValue();
                int port_tor = ((Long) linkObj.get("port_tor")).intValue();
                int port_ocs = ((Long) linkObj.get("port_ocs")).intValue();

                ret.put(tor_log, new Link(tor_log, tor_phy, port_tor, port_ocs));
            }
        }

        return ret;
    }

}
