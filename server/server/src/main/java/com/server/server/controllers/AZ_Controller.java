
package com.server.server.controllers;

import org.springframework.core.io.Resource;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/maps/Arizona")
public class AZ_Controller {
    @GetMapping(value = "/2020 Districts", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Resource> getLA2020() throws Exception {
        Resource resource = new ClassPathResource("az_2020.json");
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=" + resource.getFilename())
                .header("Access-Control-Allow-Origin","http://localhost:3000")
                .body(resource);
    }

    @GetMapping(value = "/2010 Districts", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Resource> getLA2010() throws Exception {
        Resource resource = new ClassPathResource("az_2010.json");
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=" + resource.getFilename())
                .header("Access-Control-Allow-Origin","http://localhost:3000")
                .body(resource);
    }
}