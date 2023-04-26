
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

import com.server.server.StateRepository;
import com.server.server.State;

@RestController
@RequestMapping("/map/")
public class State_Controller {
    @Autowired
    private StateRepository repository; 

    // @GetMapping(value = "/{state}/{plan}", produces = MediaType.APPLICATION_JSON_VALUE)
    // public ResponseEntity<Resource> getDistrictPlan(@PathVariable String state, @PathVariable String plan) throws Exception {
    //     System.out.println("hello");
    //     Resource resource = new ClassPathResource("md_2020_complete.json");
        
    //     // Query query = new Query();
    //     // query.addCriteria(Criteria.where("name").is(state));   
    //     System.out.println(state+" "+ plan);
    //     List<State> states =repository.findPlan(state, plan);
    //     if(states.size()>0){
    //     State gottenstate = states.get(0);
    //     System.out.println(gottenstate.getState());
    //     return ResponseEntity.ok()
    //             .header("Content-Disposition", "attachment; filename=" + resource.getFilename())
    //             .header("Access-Control-Allow-Origin","http://localhost:3000")
    //             .body(resource);
    //     }
    //     return ResponseEntity.notFound(;

    //     // return ;

    // }

    @RequestMapping(value = "/{state}/{plan}", produces="application/json")
    public Object getDistrictPlan(@PathVariable String state, @PathVariable String plan) {
        List<State> states =repository.findPlan(state, plan);
        if(states.size()>0){
            State gottenstate = states.get(0);
            return gottenstate.getState();
        }
        throw new ResponseStatusException(
                HttpStatus.NOT_FOUND, state+ " "+ plan + " not found"
        );
        
    }


}