package com.server.server;
import org.bson.json.JsonObject;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import com.fasterxml.jackson.databind.util.JSONPObject;
import org.json.simple.JSONObject;
@Document(collection = "ensembles")
public class Ensemble {
    @Id
    private String id;


    private Object plots;

    public JSONObject getEnsemble(){ 
        JSONObject json = new JSONObject();
        json.put("plots", plots);
        return json;
    }

}
