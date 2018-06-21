package pl.intelliseq.genetraps.api.dx.controllers;

import com.dnanexus.DXJob;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import pl.intelliseq.genetraps.api.dx.exceptions.DxRunnerException;
import pl.intelliseq.genetraps.api.dx.helpers.DxApiProcessManager;

import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@RestController
public class FilesController {

    private Logger log = Logger.getLogger(FilesController.class);


    @Autowired
    private DxApiProcessManager processManager;


    private String matchFileAndGetName(String filename, String regex) {
        Pattern p = Pattern.compile(regex);
        Matcher m = p.matcher(filename);
        if (m.matches()) {
            return m.group(1);
        }
        return null;
    }


    @RequestMapping(value = "/upload-both", method = RequestMethod.POST)
    public String uploadBoth(
            @RequestParam String left,
            @RequestParam String right,
            @RequestParam String sampleNumber,
            @RequestParam(required = false) String... tag) {

        String leftRegex = "(.*?)_1\\.(f(ast)?q(\\.gz)?)";
        String leftName = matchFileAndGetName(left, leftRegex);

        String rightRegex = "(.*?)_2\\.(f(ast)?q(\\.gz)?)";
        String rightName = matchFileAndGetName(right, rightRegex);

        if (leftName != null && leftName.equals(rightName)) {
            DXJob leftId = processManager.runUrlFetch(left, sampleNumber, tag);
            DXJob rightId = processManager.runUrlFetch(right, sampleNumber, tag);

            return String.format("[\"%s\",\"%s\"]", leftId.getId(), rightId.getId());
        } else {
            throw new DxRunnerException("Incompatible files");
        }
    }

    @RequestMapping(value = "/upload", method = RequestMethod.POST)
    public String upload(
            @RequestParam String url,
            @RequestParam String sampleNumber,
            @RequestParam(required = false) String... tag) {
        log.info(Arrays.toString(tag));

        return new ObjectMapper().createObjectNode().put("id", processManager.runUrlFetch(url, sampleNumber, tag).getId()).toString();
    }

    @RequestMapping(value = "/describe/{id}", method = RequestMethod.GET)
    public String describe(
            @PathVariable String id) {
        return processManager.JSONDescribe(id).toString();
    }

    @RequestMapping(value = "/fastqc", method = RequestMethod.POST)
    public String fastqc(@RequestParam String fileId) {
        return new ObjectMapper().createObjectNode().put("id", processManager.runFastqc(fileId).getId()).toString();
    }

}
