package com.server.server;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;

import com.server.server.Incumbent;

public interface IncumbentRepository extends MongoRepository<Incumbent, Integer>{

    @Query("{ 'name' : ?0 }")
    List<Incumbent> findIncumbent(String name);

}