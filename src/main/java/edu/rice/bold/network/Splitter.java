package edu.rice.bold.network;

import edu.rice.bold.network.AComponent;

import java.util.ArrayList;

/**
 * Created by xs6 on 8/15/16.
 */
public class Splitter extends AComponent {
    final private int fanout;
    final private int inport;
    final private ArrayList<Integer> outports;

    public Splitter(int fo, int in, ArrayList<Integer> outs, ComponentPool c) {
        fanout = fo;
        inport = in;
        outports = (ArrayList<Integer>) outs.clone();
        cp = c;
        isValid = true;
    }

    public int getFanout() {
        return fanout;
    }

    public int getInport() {
        return inport;
    }

    public ArrayList<Integer> getOutports() {
        return outports;
    }

    public int getOutport(int index) {
        assert (index < outports.size());
        return outports.get(index);
    }


    @Override
    public String toString() {
        return "Splitter{" +
                "fanout=" + fanout +
                ", inport=" + inport +
                ", outports=" + outports +
                ", v=" + isValid +
                '}';
    }
}
