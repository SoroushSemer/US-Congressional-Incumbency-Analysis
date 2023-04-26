
package com.server.server.controllers;

import org.springframework.core.io.Resource;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;

import java.util.List;

import org.apache.catalina.connector.Response;
import org.json.simple.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import com.server.server.Incumbent;
import com.server.server.IncumbentRepository;

@RestController
@RequestMapping("/state/")
public class Incumbent_Controller {
    @Autowired
    private IncumbentRepository repository; 

    @RequestMapping(value = "/{state}", produces="application/json")
    public Object getIncumbents(@PathVariable String state) {
        List<Incumbent> states =repository.findIncumbent(state);
        if(states.size()>0){
            Incumbent gottenstate = states.get(0);
            return gottenstate.getIncumbent();
        }
        throw new ResponseStatusException(
                HttpStatus.NOT_FOUND, state + " not found"
        );
        
    }


}