# MCP Beginner's Guide

## What is Model Context Protocol (MCP)?

Model Context Protocol (MCP) is a revolutionary standard that connects AI assistants to external tools and data sources. Think of it as a bridge that lets AI models like Claude, ChatGPT, or other AI systems interact with your local files, APIs, databases, and applications.

### Why MCP Matters

Before MCP, AI assistants were limited to text-only conversations. With MCP, they can:

- **Execute commands** on your computer
- **Read and write files** in your projects  
- **Call APIs** to fetch or send data
- **Access databases** and other data sources
- **Use specialized tools** like code formatters, compilers, or custom applications

### MCP vs Traditional Approaches

| Traditional AI Chat | MCP-Enhanced AI |
|-------------------|-----------------|
| Text-only responses | Can perform actions |
| No file access | Reads/writes your files |
| Can't run code | Executes code and tools |
| Static knowledge | Dynamic, real-time data |
| Manual copy/paste | Automated workflows |

## How MCP Works

MCP uses a client-server architecture:

```
AI Assistant (Client) ←→ MCP Server ←→ Your Tools/Data
     (Claude)              (Our Server)    (Notion API)
```

### The Components

1. **MCP Client**: The AI assistant (like Claude Desktop)
2. **MCP Server**: A program that provides specific tools
3. **Tools**: Functions the AI can call (like uploading files)
4. **Resources**: Data the AI can access (like file contents)

### Communication Flow

```
1. You ask AI: "Upload my notes to Notion"
   ↓
2. AI identifies this needs the upload_markdown tool
   ↓  
3. AI calls MCP server: upload_markdown(filepath="/path/to/notes.md", ...)
   ↓
4. MCP server processes request and calls Notion API
   ↓
5. MCP server returns success message to AI
   ↓
6. AI shows you the result: "Successfully uploaded to Notion at [URL]"
```

## Setting Up MCP (Step by Step)

### Prerequisites

- AI assistant that supports MCP (Claude Desktop, Cline, etc.)
- Python 3.8 or later
- Basic command line knowledge

### Installation Steps

#### 1. Install the MCP Server

```bash
# Clone the repository
git clone https://github.com/bonbonsan/markdown2notion.git
cd markdown2notion

# Install dependencies  
pip install -e .
```

#### 2. Set Up Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name: "Markdown2Notion"
4. Copy the "Internal Integration Token"
5. Create `.env` file:

```bash
echo "NOTION_TOKEN=your_token_here" > .env
```

#### 3. Grant Notion Permissions

1. Open your target Notion page
2. Click the "..." menu → "Add connections" 
3. Search for "Markdown2Notion" and select it
4. Click "Confirm"

#### 4. Configure Your AI Client

For Claude Desktop (`cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "markdown2notion": {
      "command": "python",
      "args": ["/full/path/to/markdown2notion/src/server.py"]
    }
  }
}
```

#### 5. Test the Setup

Restart your AI client and try:
> "Upload this markdown file to my Notion workspace: /path/to/file.md using parent page https://notion.so/my-page"

## Understanding MCP Tools

### What Are Tools?

Tools are functions that AI assistants can call. Each tool has:

- **Name**: Like `upload_markdown`
- **Description**: What it does
- **Parameters**: What inputs it needs
- **Return Value**: What it gives back

### Our Tools Explained

#### upload_markdown

**What it does**: Takes a Markdown file and creates a Notion page

**Why it's useful**: 
- Saves time copying/pasting content
- Preserves formatting automatically  
- Handles large files (100+ sections)
- Creates proper Notion blocks

**Example conversation**:
> **You**: "Upload my project documentation to Notion"
> 
> **AI**: "I can help you upload a Markdown file to Notion. What's the file path and which Notion page should be the parent?"
> 
> **You**: "The file is /Users/me/docs/project.md and the parent page is https://notion.so/my-workspace/abc123"
> 
> **AI**: *calls upload_markdown tool* "Successfully uploaded 'project.md' to Notion! View it at: https://notion.so/def456"

#### upload_markdown_content

**What it does**: Takes raw Markdown text and creates a Notion page

**Why it's useful**:
- Create pages from generated content
- Upload notes from conversations
- Quick page creation without files

#### Other Tools

- `list_database_pages`: See what's in a database
- `get_database_info`: Get database details

## Common MCP Concepts

### Environment Variables

Many MCP servers use environment variables for configuration:

```bash
# In your .env file
NOTION_TOKEN=secret_token_here
API_KEY=another_secret
DATABASE_URL=connection_string
```

**Why**: Keeps secrets out of code and makes configuration flexible.

### Error Handling

MCP tools can fail for various reasons:

- **File not found**: Check your file paths
- **Permission denied**: Verify API tokens and access rights
- **Network errors**: Check internet connection
- **Invalid parameters**: Review the tool documentation

### Tool Discovery

AI assistants automatically discover available tools when they connect to an MCP server. You don't need to tell the AI what tools exist - it figures this out automatically.

## Best Practices

### Security

1. **Never share tokens**: Keep `.env` files private
2. **Use specific permissions**: Grant minimal necessary access
3. **Regular rotation**: Update API tokens periodically

### File Paths

1. **Use absolute paths**: `/full/path/to/file.md` instead of `./file.md`
2. **Check existence**: Ensure files exist before referencing them
3. **Handle spaces**: Use quotes around paths with spaces

### Error Recovery

1. **Read error messages**: They usually explain what went wrong
2. **Check configuration**: Verify tokens and permissions
3. **Test small first**: Try simple cases before complex ones

## Troubleshooting Guide

### "Tool not found" Error

**Problem**: AI says it doesn't know about MCP tools

**Solutions**:
- Restart your AI client
- Check MCP server configuration
- Verify the server is running

### "Permission denied" Error

**Problem**: Can't access Notion/files

**Solutions**:
- Check Notion integration permissions
- Verify file system permissions  
- Confirm API token is correct

### "Invalid URL" Error

**Problem**: Notion URL format not recognized

**Solutions**:
- Use full URLs: `https://notion.so/page-title-id`
- Copy from browser address bar
- Don't use workspace-specific URLs

### Server Won't Start

**Problem**: MCP server fails to launch

**Solutions**:
- Check Python installation
- Verify dependencies installed
- Look at error messages in terminal

## Advanced Usage

### Batch Operations

Once you understand the basics, you can do more complex operations:

> "Upload all the .md files in my /docs folder to the Notion page at [URL], creating a separate page for each file"

### Integration with Other Tools

MCP servers can work together:

> "Read the API documentation from our codebase, summarize it, and upload the summary to our Notion knowledge base"

### Custom Workflows

Create your own workflows:

> "Every time I finish a project, I want to upload the README.md to Notion and add it to our project database"

## Next Steps

1. **Try the basic upload**: Start with a simple Markdown file
2. **Explore parameters**: Try different parent pages and databases  
3. **Read the API docs**: Understand all available tools
4. **Build workflows**: Create your own automation patterns
5. **Contribute**: Help improve the tool or create new ones

## Getting Help

- **Documentation**: Check the `/docs` folder for detailed guides
- **Error messages**: Read them carefully - they're usually helpful
- **Community**: Share experiences with other MCP users
- **GitHub Issues**: Report bugs or request features

Remember: MCP is about making AI assistants more helpful by giving them access to your tools and data. Start simple, learn gradually, and build up to more complex workflows as you get comfortable with the concepts.