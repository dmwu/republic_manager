package edu.rice.bold.jgroups;

import org.jgroups.*;
import org.jgroups.util.Util;

import java.io.*;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;

public class Sender extends ReceiverAdapter {
    final List<String> state = new LinkedList<String>();
    JChannel channel;
    String user_name = System.getProperty("user.name", "n/a");
    int msgSize, numMsg, timeLimit;
    String mode;
    byte CONFIG = 0;
    byte DATA = 1;
    byte STOP = 2;

    public static void main(String[] args) throws Exception {
        new Sender().start();
    }

    public void viewAccepted(View new_view) {
        System.out.println("** view: " + new_view);
    }

    public void receive(Message msg) {
        String line = msg.getSrc() + ": " + msg.getBuffer();
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
        sb.append("-------------------- Sender --------------------\n");
        sb.append("Date: ").append(new Date()).append("\n");
        sb.append("Run by: ").append(System.getProperty("user.name")).append("\n");
        sb.append("JGroups version: ").append(Version.description).append("\n");
        System.out.println(sb);

        try {
            BufferedReader input = new BufferedReader(new InputStreamReader(System.in));
            System.out.println("Please specify the message size in byte:");
            msgSize = Integer.parseInt(input.readLine());
            input.close();
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
        long start, end;
        int i;
        byte[] sendMsg = new byte[msgSize];

        sendMsg[0] = DATA;
        for (i = 1; i < msgSize; i++) {
            sendMsg[i] = 0;
        }
        try {
            System.out.println("Sending messages...");
            while (true) {
                Message msg = new Message(null, null, sendMsg, 0, msgSize);
                channel.send(msg);
            }
        } catch (Exception e) {
            System.err.println(e);
        }
    }
}
