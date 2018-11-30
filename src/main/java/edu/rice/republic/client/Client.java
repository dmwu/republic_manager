package edu.rice.republic.client;

import edu.rice.republic.amif.AgentManagerInterface;
import edu.rice.republic.amif.Release;
import edu.rice.republic.amif.Request;
import edu.rice.republic.amif.Response;
import org.apache.commons.cli.*;
import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashSet;
import java.util.Random;
import java.util.Set;
import java.util.UUID;

/**
 * Created by xs6 on 3/26/18.
 */
public class Client {
    public static void main(String[] args) {

        Options options = new Options();

        Option ipO = new Option("i", "controller-ip", true, "IP of controller");
        ipO.setRequired(true);
        options.addOption(ipO);

        Option portO = new Option("p", "controller-port", true, "port of controller");
        portO.setRequired(true);
        options.addOption(portO);

        Option enO = new Option("e", "experiment-name", true, "name of the experiment");
        enO.setRequired(true);
        options.addOption(enO);

        Option wnO = new Option("w", "worker-number", true, "number of workers");
        wnO.setRequired(true);
        options.addOption(wnO);

        Option idO = new Option("d", "broadcast-data-id", true, "id of the broadcast data");
        idO.setRequired(true);
        options.addOption(idO);

        Option sO = new Option("s", "broadcast-data-size", true, "size of the broadcast data");
        sO.setRequired(true);
        options.addOption(sO);

        CommandLineParser parser = new BasicParser();
        HelpFormatter formatter = new HelpFormatter();
        CommandLine cmd;

        try {
            cmd = parser.parse(options, args);
        } catch (ParseException e) {
            System.out.println(e.getMessage());
            formatter.printHelp("utility-name", options);
            System.exit(1);
            return;
        }

        String ip = cmd.getOptionValue('i');
        String port = cmd.getOptionValue('p');
        String expName = cmd.getOptionValue('e');
        String workerNum = cmd.getOptionValue('w');
        String bdid = cmd.getOptionValue('d');
        String bds = cmd.getOptionValue('s');

        TTransport transport;
        transport = new TSocket(ip, Integer.valueOf(port));
        try {
            transport.open();
        } catch (TTransportException e) {
            e.printStackTrace();
        }

        TProtocol protocol = new TBinaryProtocol(transport);
        AgentManagerInterface.Client client = new AgentManagerInterface.Client(protocol);

        try {
            perform(client, expName, Integer.valueOf(workerNum), bdid, Integer.valueOf(bds));
        } catch (TException e) {
            e.printStackTrace();
        }

        transport.close();
    }

    private static void perform(AgentManagerInterface.Client client, String expName, int workerNum, String broadcastDataID, int broadcastDataSize) throws TException {

        String master_filename = String.format("./scripts/broadcast/%s/cluster_settings/master", expName);
        String slaves_filename = String.format("./scripts/broadcast/%s/cluster_settings/slaves_%d", expName, workerNum);

        String ip_prefix_format = "[INTERNAL_NETWORK_PREFIX].50.%d";

        String master = "";
        HashSet<String> slaves = new HashSet<String>();

        try {
            String readLine = "";
            int suffix = 0;

            File f = new File(master_filename);
            BufferedReader b = new BufferedReader(new FileReader(f));
            while ((readLine = b.readLine()) != null) {
                if (readLine.length() > 0 && readLine.charAt(0) != '#') {
                    suffix = Integer.valueOf(readLine);
                    master = String.format(ip_prefix_format, suffix);
                }
            }
            assert master.length() > 1;

            File f_slaves = new File(slaves_filename);
            BufferedReader b_slaves = new BufferedReader(new FileReader(f_slaves));
            while ((readLine = b_slaves.readLine()) != null) {
                if (readLine.length() > 0 && readLine.charAt(0) != '#') {
//                    System.out.println(readLine);
                    suffix = Integer.valueOf(readLine);
                    slaves.add(String.format(ip_prefix_format, suffix));
                }
            }
            assert slaves.size() == workerNum;

        } catch (IOException e) {
            e.printStackTrace();
        }

        Random rnd = new Random();
        String rid = UUID.randomUUID().toString();
        String aid = "simple application";
        String did = String.valueOf(rnd.nextLong());
        long datasize = broadcastDataSize;
        long remainingsize = broadcastDataSize;

        do {

            Request rq = new Request(rid,
                    aid,
                    did,
                    datasize,
                    remainingsize,
                    master,
                    slaves);
            System.out.println("[REQUEST]:\t" + rq);

            Response rp = client.request(rq);
            System.out.println("[RESPONSE]:\t" + rp);

            remainingsize -= rp.acceptedsize;


            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            System.out.println("[RELEASE]\t" + rq.rqid + " " + rp.rqid);
            Release rl = new Release(rq.rqid, rp.rpid);
            client.release(rl);
        } while (remainingsize > 0);
    }

}
