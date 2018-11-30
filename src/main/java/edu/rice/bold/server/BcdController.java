package edu.rice.bold.server;

import edu.rice.bold.service.BcdService;
import edu.rice.bold.serviceImpl.BcdServiceImpl;
import org.apache.commons.cli.*;
import org.apache.commons.cli.ParseException;
import org.apache.log4j.Logger;
import org.apache.thrift.server.TServer;
import org.apache.thrift.server.TSimpleServer;
import org.apache.thrift.transport.TServerSocket;
import org.apache.thrift.transport.TServerTransport;
import org.apache.thrift.transport.TTransportException;
import org.json.simple.JSONObject;
import org.json.simple.parser.*;

import java.io.FileReader;
import java.io.IOException;

/**
 * Created by xs6 on 8/16/16.
 */
public class BcdController {
    final static Logger logger = Logger.getLogger(BcdController.class.getName());
    private static BcdService.Processor processor;
    private static String configPath = "./conf/";

    public static void main(String[] args) {
        Options options = new Options();
        options.addOption("m", "manager-port", true, "port of Republic Manager");
        options.addOption("t", "tor-port", true, "port of ToR controller");
        options.addOption("T", "tor-ip", true, "IP of ToR controller");
        options.addOption("o", "ocs-port", true, "port of OCS controller");
        options.addOption("O", "ocs-ip", true, "IP of OCS controller");

        options.addOption("s", "configure-switch", false, "talk to switch controllers");
        options.addOption("a", "asynchronous-configure", false, "asynchronous configure");
        options.addOption("c", "disconnect-circuit", false, "disconnect circuit multicast path");
        options.addOption("p", "disconnect-packet", false, "disconnect packet multicast path");

        CommandLineParser cliParser = new DefaultParser();
        HelpFormatter formatter = new HelpFormatter();
        CommandLine cmd;

        try {
            cmd = cliParser.parse(options, args);
        } catch (ParseException e) {
            e.printStackTrace();
            formatter.printHelp("utility-name", options);
            return;
        }

        String mp = cmd.getOptionValue('m');
        String tp = cmd.getOptionValue('t');
        String ti = cmd.getOptionValue('T');
        String op = cmd.getOptionValue('o');
        String oi = cmd.getOptionValue('O');

        JSONParser jsonParser = new JSONParser();
        JSONObject jsonObject_root = null;

        try {
            jsonObject_root = (JSONObject) jsonParser.parse(new FileReader(configPath + "cluster_conf.json"));
        } catch (IOException | org.json.simple.parser.ParseException e) {
            e.printStackTrace();
        }

        int splr = 0;
        if (jsonObject_root != null) {
            JSONObject jsonObject;
            jsonObject = (JSONObject) jsonObject_root.get("tor_controller");
            if (jsonObject != null) {
                if (jsonObject.get("ip") != null)
                    ti = jsonObject.get("ip").toString();
                if (jsonObject.get("port") != null)
                    tp = jsonObject.get("port").toString();
            }

            jsonObject = (JSONObject) jsonObject_root.get("ocs_controller");
            if (jsonObject != null) {
                if (jsonObject.get("ip") != null)
                    oi = jsonObject.get("ip").toString();
                if (jsonObject.get("port") != null)
                    op = jsonObject.get("port").toString();
            }

            jsonObject = (JSONObject) jsonObject_root.get("republic_manager");
            if (jsonObject != null) {
                if (jsonObject.get("port") != null)
                    mp = jsonObject.get("port").toString();
            }
            int serverPerPhyRack = Integer.parseInt(((JSONObject) jsonObject_root.get("node")).get("num_per_phy").toString());
            int logRackPerPhyRack = Integer.parseInt(((JSONObject) ((JSONObject) jsonObject_root.get("eps")).get("log")).get("num_per_phy").toString());
            splr = serverPerPhyRack / logRackPerPhyRack;
            logger.info("Republic network configuration: " + splr + " server per logical rack");
        }

        if (tp == null) {
            tp = "8010";
        }
        if (ti == null) {
            ti = "127.0.0.1";
        }
        if (op == null) {
            op = "8080";
        }
        if (oi == null) {
            oi = "127.0.0.1";
        }
        if (mp == null) {
            mp = "10080";
        }


        BcdServiceImpl server = new BcdServiceImpl(configPath, ti, Integer.parseInt(tp), oi, Integer.parseInt(op), splr, cmd.hasOption('s'), cmd.hasOption('a'), cmd.hasOption('c'), cmd.hasOption('p'));
        processor = new BcdService.Processor(server);

        String finalMp = mp;
        Runnable simple = new Runnable() {
            @Override
            public void run() {
                simple(processor, Integer.parseInt(finalMp));
            }
        };

        new Thread(simple).start();
    }

    private static void simple(BcdService.Processor processor, int mp) {
        logger.info("Republic Manager @ localhost:" + mp);

        TServerTransport serverTransport = null;
        try {
            serverTransport = new TServerSocket(mp);
        } catch (TTransportException e) {
            e.printStackTrace();
        }
        TServer server = new TSimpleServer(new TServer.Args(serverTransport).processor(processor));
        logger.info("Thrift server created");
        server.serve();
    }
}
