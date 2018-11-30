package edu.rice.republic.event;

import java.util.UUID;

/**
 * Created by xs6 on 3/27/18.
 */
public abstract class AEvent {
    UUID uuid = UUID.randomUUID();

    @Override
    public String toString() {
        return "AEvent{" +
                "uuid=" + uuid +
                '}';
    }
}
