package edu.rice.bold.jgroups;

import org.jgroups.*;
import org.jgroups.util.Util;

import java.io.*;
import java.net.InetAddress;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;

public class Receiver extends ReceiverAdapter {
    final List<String> state = new LinkedList<String>();
    JChannel channel;
    String user_name = System.getProperty("user.name", "n/a");
    int logInterval;
    int msgSize;
    int count = 0;
    int CONFIG = 0;
    int DATA = 1;
    int STOP = 2;
    double start, end, blockStart, blockEnd, duration, total, throughput, totalThruput;

    public static void main(String[] args) throws Exception {
        new Receiver().start();
    }

    public void viewAccepted(View new_view) {
        System.out.println("** view: " + new_view);
    }

    public void receive(Message msg) {
        String line = msg.getSrc() + ": " + msg.getBuffer();
        byte[] buf = msg.getBuffer();
        String interrupt;
        try {
            if (count == 0) {
                start = System.nanoTime();
                blockStart = start;
            }
            if (buf[0] == DATA) {
                count++;
            }
            if (count % logInterval == 0) {
                blockEnd = System.nanoTime();
                duration = blockEnd - blockStart;
                throughput = 8 * (msgSize / 1000) * logInterval / (duration / 1000000);
                System.out.println("Received " + count + " messages (" + duration / 1000000 + "ms, " + throughput + "Mbps)");
                blockStart = blockEnd;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        synchronized (state) {
            state.add(line);
        }
    }

    public void getState(OutputStream output) throws Exception {
        synchronized (state) {
            Util.objectToStream(state, new DataOutputStream(output));
        }
    }

    public void setState(InputStream input) throws Exception {
        List<String> list = (List<String>) Util.objectFromStream(new DataInputStream(input));
        synchronized (state) {
            state.clear();
            state.addAll(list);
        }
        System.out.println("received state (" + list.size() + " messages in chat history):");
        for (String str : list) {
            System.out.println(str);
        }
    }

    private void start() throws Exception {
        StringBuilder sb = new StringBuilder();
        sb.append("-------------------- Receiver --------------------");
        sb.append("Data: ").append(new Date()).append("\n");
        sb.append("Run by: ").append(System.getProperty("user.name")).append("\n");
        sb.append("JGroups version: ").append(Version.description).append("\n");
        System.out.println(sb);

        try {
            BufferedReader input = new BufferedReader(new InputStreamReader(System.in));
            System.out.println("Please specify the message size in byte:");
            msgSize = Integer.parseInt(input.readLine());
            System.out.println("Please specify the log frequncy (produce a log after x messages are received)");
            logInterval = Integer.parseInt(input.readLine());
        } catch (Exception e) {
            System.err.println(e);
        }

        channel = new JChannel();
        channel.setReceiver(this);
        channel.connect("ChatCluster");
        channel.getState(null, 10000);
        eventLoop();
        channel.close();
    }

    private void eventLoop() {
        String hostname = "";
        DateFormat dateFormat = new SimpleDateFormat("MM/dd/yyyy HH:mm:ss");
        try {
            hostname = InetAddress.getLocalHost().getHostName();
            BufferedWriter logFile = new BufferedWriter(new FileWriter(hostname + ".log", true));
            BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
            while (true) {
                String line = in.readLine().toLowerCase();
                if (line.startsWith("quit") || line.startsWith("exit")) {
                    end = System.nanoTime();
                    total = end - start;
                    Date date = new Date();
                    logFile.write(dateFormat.format(date) + " ");
                    totalThruput = 8 * (msgSize / 1000) * count / (total / 1000000);
                    logFile.write(" Received " + count + " messages (" + msgSize + "Bytes " + total / 1000000 + "ms, " + totalThruput + "Mbps)\n");
                    Thread.sleep(10);
                    break;
                }
            }
            in.close();
            logFile.close();
        } catch (Exception e) {
            System.err.println(e);
        }
    }
}
