package edu.rice.bold.network;

import java.util.ArrayList;

/**
 * Created by xs6 on 9/13/17.
 */
public class P2MPwR {
    int outport_num;
    ArrayList<AComponent> splitters;
    ArrayList<AComponent> relays;
    AComponent feeder;

    public P2MPwR(int outport_num, ArrayList<AComponent> splitters, ArrayList<AComponent> relays, AComponent feeder) {
        this.outport_num = outport_num;
        this.splitters = splitters;
        this.relays = relays;
        this.feeder = feeder;
    }

    public ArrayList<AComponent> getSplitters() {
        return splitters;
    }

    public ArrayList<AComponent> getRelays() {
        return relays;
    }

    public AComponent getFeeder() {
        return feeder;
    }

    @Override
    public String toString() {
        return "P2MPwR{" +
                "outport_num=" + outport_num +
                ", splitters=" + splitters +
                ", relays=" + relays +
                ", feeder=" + feeder +
                '}';
    }
}
