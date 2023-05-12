package com.server.server;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;

import com.server.server.Ensemble;

public interface EnsembleRepository extends MongoRepository<Ensemble, Integer>{

    @Query("{ 'state': ?0 }")
    List<Ensemble> findEnsemble(String state);

}