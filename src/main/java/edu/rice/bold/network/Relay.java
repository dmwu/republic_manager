package edu.rice.bold.network;

import edu.rice.bold.network.AComponent;

/**
 * Created by xs6 on 9/12/17.
 */
public class Relay extends AComponent {
    final private int port;

    public Relay(int p, ComponentPool c) {
        port = p;
        cp = c;
        isValid = true;
    }

    public int getPort() {
        return port;
    }

    @Override
    public String toString() {
        return "Relay{" +
                "port=" + port +
                ", v=" + isValid +
                '}';
    }
}
