// check the agent and the modules
var agentConfigValid = true;
setTimeout(function () {
    var nameMapping = [];
    nameMapping['W3C resource timing support'] = '3r';
    nameMapping['Support for XmlHttpRequest'] = 'x';
    nameMapping['Visually Complete'] = 'V';
    var feedbackText = 'Automatic agentConfigCheck did not work correctly.';
    var className = 'agentConfError';
    var configValElements = document.getElementsByClassName('agentConf');
    for (var k = 0; k  < configValElements.length; k++) {
        if (!checkAgentConf(configValElements[k].innerText)) {
            agentConfigValid = false;
            feedbackText = '  disabled';
            className = 'agentConfError';
        } else {
            feedbackText = '  enabled';
            className = 'agentConfOk';
        }
        var agentConfFeedback = configValElements[k].getElementsByClassName('agentConfCheck')[0];
        if (agentConfFeedback) {
           agentConfFeedback.innerText = feedbackText;
           agentConfFeedback.className = className;
        } else {
            console.log('Error while detecting the Agentconfig');
        }
    }

    //hide Example and display error message instead
    var exampleElements = document.getElementsByClassName('example'); //to support multiple examples on one page
    for (var i = 0; i < exampleElements.length; i++) {
        if (!agentConfigValid) {
            //exampleElements[i].innerText = "";
            for (var l = 0; l < exampleElements[i].children.length; l++) {
                var currentChild = exampleElements[i].children[l];
                if (currentChild.className !==  'fieldHeader') {
                    currentChild.className += ' agentConfErrorExample';
                }
            }
            var warningNode = document.createElement("div");
            warningNode.className = 'agentConfError';
            var warningText = document.createTextNode('Example doesn\'t work! Please switch on the correct agent-configuration for this example and reload this page!');
            warningNode.appendChild(warningText);
            exampleElements[i].appendChild(warningNode);
        }
    }
    function checkAgentConf(configString) {
        var configValue = configString === 'no extra modules' ? 'no extra modules' : nameMapping[configString] || undefined;
        var agentConfCorrect = true;
        if (typeof dT_ === 'undefined' || configValue === undefined) {
            console.log('AgentConfigCheck failed because not agent is present or some other internal error');
            agentConfCorrect = false;
        } else if (configValue === 'no extra modules' && typeof dT_ !== 'undefined') {     // -> returns true
            console.log('Skipped AgentConfigCheck because only default agent is needed');
        } else {
            for (var i = 0; i < configValue.length; i++) {
                if(!dT_.ism(configValue.charAt(i))) {
                    agentConfCorrect = false;
                }
            }
        }
        return agentConfCorrect;
    }
}, 0);
