
package com.server.server.controllers;

import org.springframework.core.io.Resource;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/maps/Maryland")
public class MD_Controller {
    @GetMapping(value = "/2020 Districts", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Resource> getMD2020() throws Exception {
        Resource resource = new ClassPathResource("md_2020_complete.json");
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=" + resource.getFilename())
                .header("Access-Control-Allow-Origin","http://localhost:3000")
                .body(resource);
    }

    @GetMapping(value = "/Generated Plan 1", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Resource> getMDGen1() throws Exception {
        Resource resource = new ClassPathResource("GeneratedPlan1.json");
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=" + resource.getFilename())
                .header("Access-Control-Allow-Origin","http://localhost:3000")
                .body(resource);
    }
    @GetMapping(value = "/Generated Plan 2", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Resource> getMDGen2() throws Exception {
        Resource resource = new ClassPathResource("GeneratedPlan2.json");
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=" + resource.getFilename())
                .header("Access-Control-Allow-Origin","http://localhost:3000")
                .body(resource);
    }
    @GetMapping(value = "/Generated Plan 3", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Resource> getMDGen3() throws Exception {
        Resource resource = new ClassPathResource("GeneratedPlan3.json");
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=" + resource.getFilename())
                .header("Access-Control-Allow-Origin","http://localhost:3000")
                .body(resource);
    }
}