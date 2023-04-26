package com.server.server;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;

import com.server.server.State;

public interface StateRepository extends MongoRepository<State, Integer>{

    @Query("{ 'state': ?0, 'name' : ?1 }")
    List<State> findPlan(String state, String plan);

}