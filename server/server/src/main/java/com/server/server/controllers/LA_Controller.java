package com.server.server.controllers;

import org.springframework.core.io.Resource;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LA_Controller {
    @GetMapping(value = "/la_2020", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Resource> getLA2020() throws Exception {
        Resource resource = new ClassPathResource("la_2020.json");
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=" + resource.getFilename())
                .body(resource);
    }

    @GetMapping(value = "/la_2010", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Resource> getLA2010() throws Exception {
        Resource resource = new ClassPathResource("la_2010.json");
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=" + resource.getFilename())
                .body(resource);
    }
}
