package com.server.server;
import org.bson.json.JsonObject;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import com.fasterxml.jackson.databind.util.JSONPObject;
import org.json.simple.JSONObject;
@Document(collection = "states")
public class State {
    @Id
    private String id;

    private String name;

    private Object features;
    private String type;

    public JSONObject getState(){ 
        JSONObject json = new JSONObject();
        json.put("type", type);
        json.put("features", features);
        return json;
    }

}
