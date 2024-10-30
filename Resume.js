// src/Resume.js
import { Box, Button, Container, Typography } from '@mui/material';
import axios from 'axios';
import { useState } from 'react';

const Resume = () => {
  // State to hold topic IDs and memos
  const [topics, setTopics] = useState([]);
  const [responseMessage, setResponseMessage] = useState(''); // State to hold the response message

  // Function to make requests to Flask routes
  const handleRequest = async (route) => {
    let input = '';
    if (route === 'create_topic') {
      input = prompt('Enter topic memo:');
    } else if (route === 'send_event') {
      // Prompt for event message and topic ID
      const eventMessage = prompt('Enter event message:');
      const topicId = prompt('Enter topic ID:');
      if (!eventMessage || !topicId) {
        alert('Please provide both an event message and a topic ID.');
        return;
      }
      input = { eventMessage, topicId }; // Use an object to pass both parameters
    } else if (route === 'get_topic_events') {
      input = prompt('Enter topic ID:');
    }

    try {
      // Send the appropriate request to the Flask server
      const response = await axios.get(`http://localhost:5000/${route}`, {
        params: {
          memo: route === 'create_topic' ? input : undefined,
          event_message: route === 'send_event' ? input.eventMessage : undefined,
          topic_id: route === 'send_event' ? input.topicId : route === 'get_topic_events' ? input : undefined,
        },
      });

      // Clear previous response message and set new one
      if (response.data.success) {
        // Set the topics state if the route is 'get_topic_ids'
        if (route === 'get_topic_ids') {
          setTopics(response.data.data);
        }
        // Format the response message to display the relevant information
        setResponseMessage(`Response from ${route}: ${JSON.stringify(response.data.data)}`);
      } else {
        // Handle errors returned from the Flask app
        setResponseMessage(`Error: ${response.data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error(`Error fetching from ${route}:`, error);
      setResponseMessage(`Error fetching from ${route}: ${error.message}`); // Set error message
    }
  };

  return (
    <div>
      {/* Main Section */}
      <Box sx={{ padding: '50px 0', backgroundColor: '#eceff1' }}>
        <Container>
          <Typography variant="h2" sx={{ fontFamily: 'Roboto, sans-serif', fontWeight: 'bold', color: '#263238', textAlign: 'center', marginBottom: '40px' }}>
            Joseph Cabusas
          </Typography>

          {/* Button Section */}
          <Box display="flex" flexDirection="column" alignItems="center" mt={4}>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleRequest('create_topic')}
              sx={{ padding: '10px 20px', fontSize: '1.2rem', marginBottom: '20px' }}
            >
              Create Topic
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleRequest('send_event')}
              sx={{ padding: '10px 20px', fontSize: '1.2rem', marginBottom: '20px' }}
            >
              Send Event
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleRequest('get_topic_events')}
              sx={{ padding: '10px 20px', fontSize: '1.2rem' }}
            >
              Get Topic Events
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleRequest('get_topic_ids')}
              sx={{ padding: '10px 20px', fontSize: '1.2rem', marginTop: '20px' }}
            >
              Get Topic IDs
            </Button>
          </Box>

          {/* Display Topic IDs */}
          {topics.length > 0 && (
            <Box sx={{ marginTop: '20px', padding: '10px', backgroundColor: '#ffffff', borderRadius: '5px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <Typography variant="h6" sx={{ fontFamily: 'Roboto, sans-serif', color: '#263238' }}>
                Topic IDs:
              </Typography>
              {topics.map((topic, index) => (
                <Typography key={index} sx={{ color: '#455a64' }}>
                  Topic ID: {topic.topic_id} - Memo: {topic.memo}
                </Typography>
              ))}
            </Box>
          )}

          {/* Display Response Message */}
          {responseMessage && (
            <Box sx={{ marginTop: '20px', padding: '10px', backgroundColor: '#ffffff', borderRadius: '5px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <Typography variant="h6" sx={{ fontFamily: 'Roboto, sans-serif', color: '#263238' }}>
                {responseMessage}
              </Typography>
            </Box>
          )}
        </Container>
      </Box>
    </div>
  );
};

export default Resume;
