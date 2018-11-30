package edu.rice.bold.network;

import edu.rice.bold.network.AComponent;
import edu.rice.bold.network.InOuts;

/**
 * Created by xs6 on 8/24/16.
 */
public class Feeder extends AComponent {
    final private int port;

    public Feeder(int p, ComponentPool c) {
        port = p;
        cp = c;
        isValid = true;
    }

    public int getPort() {
        return port;
    }

    @Override
    public String toString() {
        return "Feeder{" +
                "port=" + port +
                ", v=" + isValid +
                '}';
    }
}
