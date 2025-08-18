# LiveKit Agent with Knowledge Base Integration

This project implements a LiveKit agent with integrated knowledge base functionality for the N_KB_Q&A_With_StrategicNarrative_V3_Adaptive node.

## Features

- Dynamic knowledge base querying based on user interests and conversation context
- In-memory vector database for minimal latency
- PDF document processing and embedding generation
- Personalized responses based on user profile and conversation history
- Docker containerization for easy deployment
- Performance monitoring and caching

## Architecture

The implementation follows a modular architecture:

1. **KB Processor**: Handles all knowledge base operations including querying and response generation
2. **PDF Preprocessing Pipeline**: Processes PDF documents into vector embeddings
3. **Call Flow Engine**: Integrates KB functionality into the existing conversation flow
4. **Docker Configuration**: Enables easy deployment on AWS EC2

## Setup

1. Place your PDF document in the `data/` directory:
   ```
   cp /path/to/your/document.pdf data/dan_in_ippei_and_company_info.pdf
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key
   export LIVEKIT_URL=your_livekit_url
   export LIVEKIT_API_KEY=your_livekit_api_key
   export LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

4. Run the preprocessing pipeline:
   ```
   python preprocess_kb.py
   ```

5. Start the agent:
   ```
   python caller_agent.py
   ```

## Docker Deployment

1. Build the Docker image:
   ```
   docker build -t livekit-agent-kb .
   ```

2. Run the container:
   ```
   docker run -p 8080:8080 \
     -e OPENAI_API_KEY=your_openai_api_key \
     -e LIVEKIT_URL=your_livekit_url \
     -e LIVEKIT_API_KEY=your_livekit_api_key \
     -e LIVEKIT_API_SECRET=your_livekit_api_secret \
     livekit-agent-kb
   ```

## Docker Compose Deployment

1. Set environment variables in a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   LIVEKIT_URL=your_livekit_url
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

2. Run with docker-compose:
   ```
   docker-compose up
   ```

## AWS EC2 Deployment

1. Create an EC2 instance with the following specifications:
   - AMI: Amazon Linux 2 or Ubuntu 20.04
   - Instance type: t3.medium or larger
   - Storage: 20GB SSD

2. Install Docker on the EC2 instance:
   ```
   sudo yum update -y
   sudo amazon-linux-extras install docker -y
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   ```

3. Install Docker Compose:
   ```
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

4. Copy the project files to the EC2 instance:
   ```
   scp -i your-key.pem -r . ec2-user@your-ec2-instance:/home/ec2-user/livekit-agent
   ```

5. SSH into the EC2 instance and run the agent:
   ```
   cd /home/ec2-user/livekit-agent
   docker-compose up
   ```

## Monitoring

The system includes built-in performance monitoring with the following metrics:

- Query Response Time
- Embedding Search Time
- LLM Response Generation Time
- Cache Hit Rate
- Memory Usage

Metrics are logged periodically and can be viewed in the application logs.

## Testing

To test the implementation:

1. Run the unit tests:
   ```
   python -m pytest tests/
   ```

2. Test the KB processor directly:
   ```
   python kb_processor.py
   ```

## Troubleshooting

### PDF Processing Issues

If the PDF preprocessing fails, ensure the PDF file is not corrupted and is in a supported format.

### KB Query Performance

If KB queries are slow, check:
- Network connectivity to OpenAI API
- Memory usage on the server
- Cache hit rate in the logs

### Docker Issues

If Docker containers fail to start, check:
- Environment variables are properly set
- Required ports are available
- Sufficient disk space is available

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.
