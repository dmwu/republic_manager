package edu.rice.bold.network;

import java.util.Set;

/**
 * Created by xs6 on 11/21/17.
 */
public class InOuts {
    Link in;
    Set<Link> outs;

    public InOuts(Link in, Set<Link> outs) {
        this.in = in;
        this.outs = outs;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        InOuts inOuts = (InOuts) o;

        if (in != null ? !in.equals(inOuts.in) : inOuts.in != null) return false;
        return outs != null ? outs.equals(inOuts.outs) : inOuts.outs == null;
    }

    @Override
    public int hashCode() {
        int result = in != null ? in.hashCode() : 0;
        result = 31 * result + (outs != null ? outs.hashCode() : 0);
        return result;
    }
}
