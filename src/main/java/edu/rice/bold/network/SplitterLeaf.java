package edu.rice.bold.network;

import edu.rice.bold.network.Splitter;

/**
 * Created by xs6 on 9/13/17.
 */
public class SplitterLeaf {
    Splitter splt;
    int port;

    public SplitterLeaf(Splitter splt, int port) {
        this.splt = splt;
        this.port = port;
    }

    public Splitter getSplitter() {
        return splt;
    }

    public int getOutport() {
        return port;
    }

    @Override
    public String toString() {
        return "SplitterLeaf{" +
                "splt=" + splt +
                ", port=" + port +
                '}';
    }
}
