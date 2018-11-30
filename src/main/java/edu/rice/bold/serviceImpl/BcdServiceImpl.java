package edu.rice.bold.serviceImpl;

import edu.rice.bold.network.*;
import edu.rice.bold.service.BcdInfo;
import edu.rice.bold.service.BcdService;
import edu.rice.bold.service.PushReply;
import edu.rice.bold.service.PushReplyCmd;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.log4j.Logger;
import org.apache.thrift.TException;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.*;

/**
 * Created by xs6 on 8/14/16.
 */
public class BcdServiceImpl implements BcdService.Iface {
    private final static Logger logger = Logger.getLogger(BcdServiceImpl.class.getName());
    private final static String MULTICAST_ADDR_PREFIX = "238.238.238.";
    private final static int DEFAULT_MULTICAST_RULE_PRIORITY = 4;
    private final static String TOR_ADD_PATH = "/stats/flowentry/add";
    private final static String TOR_DEL_STRICT_PATH = "/stats/flowentry/delete_strict";
    private final static String ACL_TEMPLATE_FORMAT = "{\n" +
            "  \"dpid\": %d,\n" +
            "  \"table_id\": 60,\n" +
            "  \"priority\": 4,\n" +
            "  \"match\": {\n" +
            "    \"in_port\": %d,\n" +
            "    \"eth_type\": 0x0800,\n" +
            "    \"vlan_vid\": %d,\n" +
            "    \"ipv4_dst\": \"%s\"\n" +
            "  },\n" +
            "  \"actions\": [\n" +
            "    {\n" +
            "      \"type\": \"WRITE_ACTIONS\",\n" +
            "      \"actions\": [\n" +
            "        {\n" +
            "          \"type\": \"SET_QUEUE\",\n" +
            "          \"queue_id\": %d\n" +
            "        },\n" +
            "        {\n" +
            "          \"type\": \"GROUP\",\n" +
            "          \"group_id\": 0x%08x\n" +
            "        }\n" +
            "      ]\n" +
            "    }\n" +
            "  ]" +
            "}";

    private final static String OCS_ADD_PATH = "/fiber/ent_crs";
    private final static String OCS_DEL_PATH = "/fiber/del_crs";
    private final static String OCS_TEMPLATE_FORMAT = "{\"inport\":[%s], \"outport\":[%s]}";
    private final static int SPLITTER_FANOUT = 4;

    private static int xid = 0;
    private static URIBuilder ocs_add_uri;
    private static URIBuilder ocs_del_uri;
    private static URIBuilder tor_add_uri;
    private static URIBuilder tor_del_strict_uri;

    final private Map<String, Server> serverMap;
    final private Map<Integer, Link> linkMap;

    final private Map<Integer, ComponentPool> splitterPool;
    final private ComponentPool feederPool;
    final private ComponentPool relayPool;

    final private int serverPerTor;
    final private HashMap<Integer, Resource> xidResourceMap;
    final private HashMap<InOuts, P2MPwR> iosP2MPMap;
    final private HashMap<Server, Set<Server>> senderReceiversMap;

    private boolean configureSwitch;
    private boolean asynchronousConfigure;
    private boolean disconnectCircuit;
    private boolean disconnectPacket;

    private final Object oo;
    private final Object to;
    private URIBuilder ou;
    private String oc;
    private URIBuilder tu;
    private List<String> tc;

    public BcdServiceImpl(String config_dir, String ti, int tp, String oi, int op, int spr, boolean cs, boolean as, boolean dc, boolean dp) {
        /*
        1. load system configuration
         */
        serverPerTor = spr;

        configureSwitch = cs;
        asynchronousConfigure = as;
        disconnectCircuit = dc;
        disconnectPacket = dp;

        /*
        2. build the resource pool
        .server input pool .isconflict()
        .server output pool .isconflict()
        .circuit input pool .isconflict()
        .circuit output pool .isconflict()
        .p2mpc pool .
        .feeder pool
        .relay pool
         */
        serverMap = Server.load(config_dir + "server.json");
        linkMap = Link.load(config_dir + "switch.json");

        splitterPool = ComponentPool.loadSplitter(config_dir + "splitter.json");
        feederPool = ComponentPool.loadFeeder(config_dir + "feeder.json");
        relayPool = ComponentPool.loadRelay(config_dir + "relay.json");

        xidResourceMap = new HashMap<>();
        iosP2MPMap = new HashMap<>();
        senderReceiversMap = new HashMap<>();

        // create HttpClient for OCS controller
        ocs_add_uri = new URIBuilder().setScheme("http").setHost(oi).setPort(op).setPath(OCS_ADD_PATH);
        ocs_del_uri = new URIBuilder().setScheme("http").setHost(oi).setPort(op).setPath(OCS_DEL_PATH);

        // create HttpClient for TOR controller
        tor_add_uri = new URIBuilder().setScheme("http").setHost(ti).setPort(tp).setPath(TOR_ADD_PATH);
        tor_del_strict_uri = new URIBuilder().setScheme("http").setHost(ti).setPort(tp).setPath(TOR_DEL_STRICT_PATH);

        oo = new Object();
        OCSAgent oa = new OCSAgent();
        oa.start();

        to = new Object();
        TORAgent ta = new TORAgent();
        ta.start();

        logger.info(this.getClass().getSimpleName() + " is created:\t" + "tor @ " + ti + ":" + tp + "" + "\tocs @ " + oi + ":" + op);
    }

    @Override
    public PushReply push(String master, Set<String> slaves, BcdInfo data) throws TException {
        long a = System.nanoTime();
        logger.info("=> request received. xid[" + xid + "], master:" + master + "\t|slaves:" + slaves.toString() + "\t|bcdinfo:" + data.toString());

        /*
        1. build the representation of the request
         */
        Resource rsrc;
        // links between ToR and servers
        // master node
        Server serverMaster = serverMap.get(master);
        // slave nodes
        HashSet<Server> downServers = new HashSet<>();
        HashMap<Integer, ArrayList<Server>> torDstSlaves = new HashMap<>();
        boolean isToRConnected = false;
        for (String slave : slaves) {
            Server serverSlave = serverMap.get(slave);
            int torDst = serverSlave.getTorLog();
            if (torDstSlaves.containsKey(torDst)) {
                torDstSlaves.get(torDst).add(serverSlave);
            } else {
                ArrayList<Server> slaveList = new ArrayList<>();
                slaveList.add(serverSlave);
                torDstSlaves.put(torDst, slaveList);
            }
            downServers.add(serverSlave);
        }
        if (!disconnectPacket) {
            isToRConnected = isPacketConnected(serverMaster, downServers);
            if (isToRConnected)
                logger.info("ToR is still valid. xid[" + xid + "]");
        }

        // links between ToR and circuit switch
        // optical path
        int numOuts = torDstSlaves.containsKey(serverMaster.getTorLog()) ? torDstSlaves.size() - 1 : torDstSlaves.size();
        Link upLink = null;
        HashSet<Link> downLinks = null;
        InOuts ios = null;
        P2MPwR p2mp = null;
        boolean isP2MPConnected = false;
        if (numOuts == 0) { // no optical
            rsrc = new Resource(serverMaster, downServers);
        } else { // optical
            // optical path from tor to ocs
            upLink = linkMap.get(serverMaster.getTorLog());
            // optical paths from ocs to tor
            downLinks = new HashSet<>();
            for (Integer tor : torDstSlaves.keySet()) {
                if (tor != serverMaster.getTorLog()) {
                    Link linkDst = linkMap.get(tor);
                    downLinks.add(linkDst);
                }
            }

            ios = new InOuts(upLink, downLinks);
            if (!disconnectCircuit) {
                isP2MPConnected = iosP2MPMap.containsKey(ios);
                if (isP2MPConnected) {
                    p2mp = iosP2MPMap.get(ios);
                    logger.info("p2mp is still valid. xid[" + xid + "]");
                } else {
                    p2mp = createP2MPwR(numOuts, splitterPool.get(SPLITTER_FANOUT), relayPool, feederPool); // get required resources to build InOuts
                }
            } else { // InOuts does not exist
                p2mp = createP2MPwR(numOuts, splitterPool.get(SPLITTER_FANOUT), relayPool, feederPool); // get required resources to build InOuts
            }
            rsrc = new Resource(serverMaster, downServers, upLink, downLinks, p2mp);
        }

        /*
        2. check if the request is feasible (if server-in, server-out, circuit-in, circuit-out conflict)
         */
        boolean feasible = rsrc.isFeasible();
        logger.info("checking resource availability took [" + (System.nanoTime() - a) / 1000.0 / 1000.0 + "]ms [" + feasible + "]\t" + data);
        if (!feasible) {
            return new PushReply(xid++, PushReplyCmd.POSTPONE);
        }

        /*
        3. reserve the resource and update the multicast path
         */
        xidResourceMap.put(xid, rsrc);
        rsrc.acquire(iosP2MPMap);
        if (rsrc.isUseOptical()) { // setup circuit path
            iosP2MPMap.put(ios, p2mp);
            if (!isP2MPConnected) {
                ArrayList<String> ocsCmd = connectP2MP(upLink, downLinks, p2mp);
                rsrc.setOcsCmd(ocsCmd);
            }
        }

        if (!isToRConnected) {
            senderReceiversMap.put(serverMaster, downServers);
            Map<Integer, ArrayList<String>> torCmd = connectToR(serverMaster, torDstSlaves);
            rsrc.setTorCmd(torCmd);
        }

        logger.info("<= request took [" + (System.nanoTime() - a) / 1000.0 / 1000.0 + "]ms. xid[" + xid + "]\t" + data);
        return new PushReply(xid++, PushReplyCmd.PUSH);
    }

    private boolean isPacketConnected(Server sender, Set<Server> receivers) {
        if (senderReceiversMap.containsKey(sender)) {
            Set<Server> receivers_ = senderReceiversMap.get(sender);
            for (Server r : receivers_) {
                if (!receivers.contains(r)) {
                    return false;
                }
            }
            for (Server r : receivers) {
                if (!receivers_.contains(r)) {
                    return false;
                }
            }
        } else {
            return false;
        }
        return true;
    }

    @Override
    public void unpush(int xid) throws TException {
        logger.info("=> release received. " + "xid[" + xid + "]");
        Resource rsrc = null;
        long a = System.nanoTime();
        if (xidResourceMap.containsKey(xid)) {
            rsrc = xidResourceMap.remove(xid);
            disconnect(rsrc);
        } else if (xid < 0) { // release everything
            for (Integer i : xidResourceMap.keySet()) {
                rsrc = xidResourceMap.get(i);
                disconnect(rsrc);
            }
            xidResourceMap.clear();
        }
        logger.info("<= release took [" + (System.nanoTime() - a) / 1000.0 / 1000.0 + "]ms. xid[" + xid + "]");
    }

    private void disconnect(Resource rsrc) {
        rsrc.release();
        if (disconnectPacket) {
            disconnectToR(rsrc.getTorCmd());
        }
        if (disconnectCircuit) {
            if (rsrc.isUseOptical()) {
                disconnectOCS(rsrc.getOcsCmd());
            }
        }
    }

    private P2MPwR createP2MPwR(int outport_num, ComponentPool splitterPool, ComponentPool relayPool, ComponentPool feederPool) {
        // given fanout of P2MP get the number of splitters
        int splitter_num = Math.max(1, (int) Math.ceil((outport_num - 1.0) / (SPLITTER_FANOUT - 1)));

        ArrayList<AComponent> splitters = splitterPool.getValid(splitter_num);
        if (splitters == null) {
            logger.warn("no splitter");
            return null;
        }
        ArrayList<AComponent> relays = relayPool.getValid(splitter_num - 1);
        AComponent feeder = feederPool.getValid(1).get(0);
        if (feeder == null) {
            logger.warn("no feeder");
            return null;
        }
        return new P2MPwR(outport_num, splitters, relays, feeder);
    }

    private ArrayList<String> connectP2MP(Link upLink, HashSet<Link> downLinks, P2MPwR p2mpwr) {
        ArrayList<Integer> inportList = new ArrayList<Integer>();
        ArrayList<Integer> outportList = new ArrayList<Integer>();
        ArrayList<String> commands = new ArrayList<String>();

        // build the p2mp tree (internal optimal path)
        StringBuilder sb = new StringBuilder();
        ArrayList<SplitterLeaf> splitterLeaves = new ArrayList<>(SPLITTER_FANOUT * p2mpwr.getSplitters().size());
        assert (p2mpwr.getSplitters().size() == p2mpwr.getRelays().size() + 1);
        Splitter rootSplitter = (Splitter) (p2mpwr.getSplitters().get(0));
        for (int j = 0; j < rootSplitter.getFanout(); j++) {
            splitterLeaves.add(new SplitterLeaf(rootSplitter, rootSplitter.getOutport(j)));
        }
        sb.append("[p2mpc]:");
        for (int i = 1; i < p2mpwr.getSplitters().size(); i++) {
            Splitter curSplitter = (Splitter) (p2mpwr.getSplitters().get(i));
            SplitterLeaf curSplitterLeaf = splitterLeaves.remove(0);

            inportList.add(curSplitterLeaf.getOutport());
            outportList.add(((Relay) (p2mpwr.getRelays().get(i - 1))).getPort());
            inportList.add(((Relay) (p2mpwr.getRelays().get(i - 1))).getPort());
            outportList.add(curSplitter.getInport());

            sb.append("(" + curSplitterLeaf.getOutport() + "->" + ((Relay) (p2mpwr.getRelays().get(i - 1))).getPort() + "),");
            sb.append("(" + ((Relay) (p2mpwr.getRelays().get(i - 1))).getPort() + "->" + curSplitter.getInport() + "),");

            for (int j = 0; j < curSplitter.getFanout(); j++) {
                splitterLeaves.add(new SplitterLeaf(curSplitter, curSplitter.getOutport(j)));
            }
        }

        // the feeder
        inportList.add(((Feeder) (p2mpwr.getFeeder())).getPort());
        outportList.add(upLink.getPortOcs());
        sb.append("[feeder]:(" + ((Feeder) (p2mpwr.getFeeder())).getPort() + "->" + upLink.getPortOcs() + "),");

        // optical path from tor to ocs
        inportList.add(upLink.getPortOcs());
        outportList.add(rootSplitter.getInport());
        sb.append("[tor->ocs]:(" + upLink.getPortOcs() + "->" + rootSplitter.getInport() + "),");

        // optical paths from ocs to tor
        for (Link downLink : downLinks) {
            if (downLink.getTorLog() != upLink.getTorLog()) {
                SplitterLeaf curSplitterLeaf = splitterLeaves.remove(0);
                inportList.add(curSplitterLeaf.getOutport());
                outportList.add(downLink.getPortOcs());
                sb.append("[ocs->tor]:(" + curSplitterLeaf.getOutport() + "->" + downLink.getPortOcs() + ")");
            }
        }
        logger.info(sb.toString());
        String cmd = String.format(OCS_TEMPLATE_FORMAT, convertListToStr(inportList), convertListToStr(outportList));
        if (asynchronousConfigure) {
            synchronized (oo) {
                oc = cmd;
                ou = ocs_add_uri;
                oo.notify();
            }
        } else {
            modPath(cmd, ocs_add_uri);
        }
        commands.add(cmd);

        return commands;
    }

    private String convertListToStr(ArrayList<Integer> ports) {
        StringBuilder sb = new StringBuilder();
        for (Integer i : ports) {
            sb.append(i);
            sb.append(',');
        }
        return sb.substring(0, sb.length() - 1);
    }

    private void disconnectOCS(List<String> cmdList) {
        for (String cmd : cmdList) {
            logger.debug(cmd);
            if (asynchronousConfigure) {
                synchronized (oo) {
                    oc = cmd;
                    ou = ocs_del_uri;
                    oo.notify();
                }
            } else {
                modPath(cmd, ocs_del_uri);
            }
        }
    }

    private Map<Integer, ArrayList<String>> connectToR(Server master, Map<Integer, ArrayList<Server>> slaves) {
        Set<Integer> ToRs = slaves.keySet();
        String multicast_ip = MULTICAST_ADDR_PREFIX + master.getIp().substring(master.getIp().lastIndexOf('.') + 1, master.getIp().length());

        HashMap<Integer, ArrayList<String>> commands = new HashMap<Integer, ArrayList<String>>();
        List<String> cmds = new ArrayList<String>();

        String lastCmd = null;

        boolean last;
        for (Integer tor : ToRs) {
            ArrayList<Server> slavesInToR = slaves.get(tor);
            int group_id = 0;
            group_id |= 3 << 28;
            group_id |= tor << 16;
            for (Server s : slavesInToR) {
                group_id |= 1 << s.getRackIdx();
            }
            int inport;
            if (tor != master.getTorLog()) { // ToR not having the master
                inport = linkMap.get(tor).getPortTor();
                last = false;
            } else { // ToR having the master
                group_id |= 1 << serverPerTor;
                inport = master.getPort();
                last = true;
            }
            // send message to (tor, group_id, master_multicast_ip)
            int phy_tor = slavesInToR.get(0).getTorPhy();
            String cmd = String.format(ACL_TEMPLATE_FORMAT, phy_tor, inport, tor, multicast_ip, DEFAULT_MULTICAST_RULE_PRIORITY, group_id);
            addCommand(commands, phy_tor, cmd);
            if (last) {
                lastCmd = cmd;
            } else {
                cmds.add(cmd);
            }
        }

        if (!slaves.containsKey(master.getTorLog())) { // ToR having the master but no receiver
            int group_id = 0;
            group_id |= 3 << 28;
            group_id |= master.getTorLog() << 16;
            group_id |= 1 << serverPerTor;
            last = true;
            // send message to (tor, group_id, master_multicast_ip)
            int phy_tor = master.getTorPhy();
            String cmd = String.format(ACL_TEMPLATE_FORMAT, phy_tor, master.getPort(), master.getTorLog(), multicast_ip, DEFAULT_MULTICAST_RULE_PRIORITY, group_id);
            addCommand(commands, phy_tor, cmd);
            if (last) {
                lastCmd = cmd;
            } else {
                cmds.add(cmd);
            }
        }
        cmds.add(lastCmd);
System.out.println(cmds);
        if (asynchronousConfigure) {
            synchronized (to) {
                tc = cmds;
                tu = tor_add_uri;
                to.notify();
            }
        } else {
            modPaths(cmds, tor_add_uri);
        }
        return commands;
    }

    private void addCommand(Map<Integer, ArrayList<String>> cmdMap, int phy_tor, String cmd) {
        if (cmdMap.containsKey(phy_tor)) {
            cmdMap.get(phy_tor).add(cmd);
        } else {
            ArrayList<String> cmdList = new ArrayList<String>();
            cmdList.add(cmd);
            cmdMap.put(phy_tor, cmdList);
        }
    }

    private void disconnectToR(Map<Integer, ArrayList<String>> cmdMap) {
        List<String> cmds = new ArrayList<>();
        for (Integer phy_tor : cmdMap.keySet()) {
            for (String c : cmdMap.get(phy_tor)) {
                cmds.add(c);
            }
        }
        if (asynchronousConfigure) {
            synchronized (to) {
                tc = cmds;
                tu = tor_del_strict_uri;
                to.notify();
            }
        } else {
            modPaths(cmds, tor_del_strict_uri);
        }
    }

    private void modPaths(List<String> cmds, URIBuilder uri) {
        if (cmds == null || cmds.size() == 0) {
            return;
        }

        HttpClient httpClient = HttpClientBuilder.create().build();
        for (String cmd : cmds) {
            HttpPost post = new HttpPost(uri.toString());
            post.addHeader("Content-type", "application/json");

            StringEntity cmdE = null;
            try {
                cmdE = new StringEntity(cmd);
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }
            post.setEntity(cmdE);
            if (configureSwitch) {
                sendMsgs(httpClient, post);
            }
        }
    }

    private void modPath(String cmd, URIBuilder uri) {
        if (cmd == null) {
            return;
        }

        HttpClient httpClient = HttpClientBuilder.create().build();
        HttpPost post = new HttpPost(uri.toString());
        post.addHeader("Content-type", "application/json");

        StringEntity cmdE = null;
        try {
            cmdE = new StringEntity(cmd);
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        post.setEntity(cmdE);
        if (configureSwitch) {
            sendMsg(httpClient, post);
        }
    }

    private HttpResponse sendMsg(HttpClient client, HttpPost post) {
        HttpResponse response = null;
        try {
            response = client.execute(post);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return response;
    }

    private HttpResponse sendMsgs(HttpClient client, HttpPost post) {
        HttpResponse response = null;
        try {
            response = client.execute(post);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return response;
    }

    private class OCSAgent extends Thread {
        @Override
        public void run() {
            try {
                while (true) {
                    synchronized (oo) {
                        oo.wait();
                        long a = System.nanoTime();
                        modPath(oc, ou);
                        logger.info("OCS control took [" + (System.nanoTime() - a) / 1000.0 / 1000.0 + "]ms " + oc + " oo:" + ou.toString());
                    }
                }
            } catch (InterruptedException e) {
                e.printStackTrace();

            }
        }
    }

    private class TORAgent extends Thread {
        @Override
        public void run() {
            try {
                while (true) {
                    synchronized (to) {
                        to.wait();
                        long a = System.nanoTime();
                        modPaths(tc, tu);
                        logger.info("ToR control took [" + (System.nanoTime() - a) / 1000.0 / 1000.0 + "]ms " + tc
                                .size() + " to:" + tu.toString());
                    }
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
