package com.server.server.controllers;

import org.springframework.core.io.Resource;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Controller
public class LA_Controller {

    @GetMapping(value = "/la_2020", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getGeoJSON() throws IOException {
        Resource resource = new ClassPathResource("la_2020.json");
        byte[] bytes = resource.getInputStream().readAllBytes();
        String geoJsonString = new String(bytes, StandardCharsets.UTF_8);
        return ResponseEntity.ok(geoJsonString);
    }
}
