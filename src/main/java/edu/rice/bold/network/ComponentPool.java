package edu.rice.bold.network;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.FileReader;
import java.io.IOException;
import java.util.*;

/**
 * Created by xs6 on 11/22/17.
 */
public class ComponentPool {
    public LinkedHashSet<AComponent> pool;

    public ComponentPool(LinkedHashSet<AComponent> p) {
        pool = p;
    }

    public void access(AComponent t) {
        pool.remove(t);
        pool.add(t);
    }

    public ArrayList<AComponent> getValid(int num) {
        ArrayList<AComponent> ret = new ArrayList<>();
        for (AComponent t : pool) {
            if (t.isValid()) {
                ret.add(t);
            }
            if (ret.size() == num) {
                return ret;
            }
        }
        return null;
    }

    public static ComponentPool loadFeeder(String filename) {
        JSONParser parser = new JSONParser();
        JSONArray jsonList = null;
        try {
            jsonList = (JSONArray) parser.parse(new FileReader(filename));
        } catch (IOException | ParseException e) {
            e.printStackTrace();
        }

        LinkedHashSet<AComponent> ret = new LinkedHashSet<>();
        ComponentPool cp = new ComponentPool(ret);
        if (jsonList != null) {
            Iterator<JSONObject> iterator = (Iterator<JSONObject>) jsonList.iterator();
            while (iterator.hasNext()) {
                JSONObject serverObj = iterator.next();

                int port = ((Long) serverObj.get("port")).intValue();
                ret.add(new Feeder(port, cp));
            }
        }
        return cp;
    }

    public static ComponentPool loadRelay(String filename) {
        JSONParser parser = new JSONParser();
        JSONArray jsonList = null;
        try {
            jsonList = (JSONArray) parser.parse(new FileReader(filename));
        } catch (IOException | ParseException e) {
            e.printStackTrace();
        }

        LinkedHashSet<AComponent> ret = new LinkedHashSet<>();
        ComponentPool cp = new ComponentPool(ret);
        if (jsonList != null) {
            Iterator<JSONObject> iterator = (Iterator<JSONObject>) jsonList.iterator();
            while (iterator.hasNext()) {
                JSONObject serverObj = iterator.next();

                int port = ((Long) serverObj.get("ocs_port")).intValue();
                ret.add(new Relay(port, cp));
            }
        }

        return cp;
    }

    public static Map<Integer, ComponentPool> loadSplitter(String filename) {
        JSONParser parser = new JSONParser();
        JSONObject jsonObject = null;
        try {
            jsonObject = (JSONObject) parser.parse(new FileReader(filename));
        } catch (IOException | ParseException e) {
            e.printStackTrace();
        }

        HashMap<Integer, ComponentPool> cpMap = new HashMap<>();
        int fanout = 1;
        for (int i = 0; i < 10; i++) {
            assert jsonObject != null;
            JSONArray splitterList = (JSONArray) jsonObject.get(Integer.toString(fanout));
            if (splitterList != null) {
                LinkedHashSet<AComponent> ret = new LinkedHashSet<>();
                ComponentPool cp = new ComponentPool(ret);
                Iterator<JSONObject> iterator = (Iterator<JSONObject>) splitterList.iterator();
                while (iterator.hasNext()) {
                    JSONObject splitterObj = iterator.next();
                    int in = ((Long) splitterObj.get("in")).intValue();

                    ArrayList<Integer> outs = new ArrayList<Integer>();
                    JSONArray outList = (JSONArray) splitterObj.get("out");
                    Iterator<Long> outIterator = (Iterator<Long>) outList.iterator();
                    while (outIterator.hasNext()) {
                        outs.add((outIterator.next()).intValue());
                    }
                    ret.add(new Splitter(fanout, in, outs, cp));
                }
                cpMap.put(fanout, cp);
            }
            fanout <<= 1;
        }
        return cpMap;
    }

    @Override
    public String toString() {
        return "ComponentPool{" +
                "pool=" + pool +
                '}';
    }
}
