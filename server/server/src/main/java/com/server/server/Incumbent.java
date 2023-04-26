package com.server.server;
import org.bson.json.JsonObject;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import com.fasterxml.jackson.databind.util.JSONPObject;
import org.json.simple.JSONObject;
@Document(collection = "incumbents")
public class Incumbent {
    @Id
    private String id;

    private String name;

    private Object coords;
    private Object incumbents;
    private int zoom;
    private String summary;
    public JSONObject getIncumbent(){ 
        JSONObject json = new JSONObject();
        json.put("name", name);
        json.put("incumbents", incumbents);
        json.put("coords", coords);
        json.put("zoom", zoom);
        json.put("summary", summary);
        return json;
    }

}
