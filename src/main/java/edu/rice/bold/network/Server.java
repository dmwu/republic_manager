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

/**
 * Created by xs6 on 8/15/16.
 */
public class Server {
    final private String ip;
    final private int port;
    final private int torLog;
    final private int torPhy;
    final private int rackIdx;
    private boolean upValid;
    private boolean downValid;

    public Server(String ip, int port, int tor_log, int tor_phy, int rackIdx) {
        this(ip, port, tor_log, tor_phy, rackIdx, true);
    }

    public Server(String ip, int port, int tor_log, int tor_phy, int rackIdx, boolean valid) {
        this.ip = ip;
        this.port = port;
        this.torLog = tor_log;
        this.torPhy = tor_phy;
        this.rackIdx = rackIdx;
        this.upValid = valid;
        this.downValid = valid;
    }

    public String getIp() {
        return ip;
    }

    public int getPort() {
        return port;
    }

    public int getTorLog() {
        return torLog;
    }

    public int getTorPhy() {
        return torPhy;
    }

    public int getRackIdx() {
        return rackIdx;
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

    public void acquireUpServer() {
        setUpValid(false);
    }

    public void releaseUpServer() {
        setUpValid(true);
    }

    public void acquireDownServer() {
        setDownValid(false);
    }

    public void releaseDownServer() {
        setDownValid(true);
    }

    @Override
    public String toString() {
        return "Server{" +
                "ip='" + ip + '\'' +
                ", port=" + port +
                ", torLog=" + torLog +
                ", torPhy=" + torPhy +
                ", rackIdx=" + rackIdx +
                ", upValid=" + upValid +
                ", downValid=" + downValid +
                '}';
    }

    public static Map<String, Server> load(String filename) {
        JSONParser parser = new JSONParser();
        JSONArray jsonList = null;
        try {
            jsonList = (JSONArray) parser.parse(new FileReader(filename));
        } catch (IOException | ParseException e) {
            e.printStackTrace();
        }

        HashMap<String, Server> ret = new HashMap<String, Server>();
        if (jsonList != null) {
            Iterator<JSONObject> iterator = (Iterator<JSONObject>) jsonList.iterator();
            while (iterator.hasNext()) {
                JSONObject serverObj = iterator.next();

                String ip = (String) serverObj.get("ip");
                int port = ((Long) serverObj.get("port")).intValue();
                int tor_log = ((Long) serverObj.get("tor_log")).intValue();
                int tor_phy = ((Long) serverObj.get("tor_phy")).intValue();
                int rack_idx = ((Long) serverObj.get("rack_idx")).intValue();

                ret.put(ip, new Server(ip, port, tor_log, tor_phy, rack_idx));
            }
        }

        return ret;
    }
}
