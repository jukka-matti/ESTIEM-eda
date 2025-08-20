"""ESTIEM EDA MCP Server for Statistical Process Control.

This module implements the Model Context Protocol (MCP) server that provides
exploratory data analysis tools for Lean Six Sigma education.
"""

import json
import logging
import sys
from typing import Any

import numpy as np


class MCPJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MCP responses."""

    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class ESTIEMMCPServer:
    """MCP Server for ESTIEM EDA Statistical Tools.

    Implements MCP protocol v1.0 for exploratory data analysis tools
    used in Lean Six Sigma education.
    """

    def __init__(self):
        """Initialize the MCP server with tools and configuration."""
        self.protocol_version = "2025-06-18"
        self.server_info = {
            "name": "estiem-eda",
            "version": "3.0.0",
            "description": "Professional Six Sigma toolkit with 3 core analysis tools",
        }
        self.setup_logging()
        self.initialize_tools()

    def setup_logging(self) -> None:
        """Configure logging to stderr to not interfere with stdio."""
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stderr)],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("ESTIEM EDA MCP Server initializing...")

    def initialize_tools(self) -> None:
        """Initialize the 3 core professional statistical tools."""
        self.tools = {}

        # Process Analysis Tool (comprehensive)
        from .tools.process_analysis import ProcessAnalysisTool

        self.tools["process_analysis"] = ProcessAnalysisTool()
        self.logger.info("✅ Process Analysis tool loaded")

        # ANOVA Tool (group comparison)
        from .tools.anova import ANOVATool

        self.tools["anova_boxplot"] = ANOVATool()
        self.logger.info("✅ ANOVA Analysis tool loaded")

        # Pareto Tool (priority analysis)
        from .tools.pareto import ParetoTool

        self.tools["pareto_analysis"] = ParetoTool()
        self.logger.info("✅ Pareto Analysis tool loaded")

        self.logger.info(
            f"🚀 Professional Six Sigma toolkit ready with {len(self.tools)} core tools"
        )

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Route JSON-RPC requests to appropriate handlers.

        Args:
            request: JSON-RPC request dictionary.

        Returns:
            Response dictionary following JSON-RPC format.
        """
        method = request.get("method")
        params = request.get("params", {})

        self.logger.debug(f"Handling request: method={method}")

        handlers = {
            "initialize": self.handle_initialize,
            "initialized": self.handle_initialized,
            "tools/list": self.handle_list_tools,
            "tools/call": self.handle_call_tool,
            "notifications/cancelled": self.handle_cancelled,
        }

        handler = handlers.get(method)
        if handler:
            try:
                return handler(params)
            except Exception as e:
                self.logger.error(f"Handler error for {method}: {e}")
                return self.error_response(-32603, f"Internal error: {str(e)}")
        else:
            self.logger.error(f"Unknown method: {method}")
            return self.error_response(-32601, f"Method not found: {method}")

    def handle_initialize(self, params: dict) -> dict:
        """Handle initialization request.

        Args:
            params: Initialization parameters from client.

        Returns:
            Server capabilities and information.
        """
        self.logger.info("Handling initialize request")

        # Log client information for debugging
        client_info = params.get("clientInfo", {})
        client_protocol = params.get("protocolVersion", "unknown")
        self.logger.info(
            f"Client: {client_info.get('name', 'unknown')} v{client_info.get('version', 'unknown')}"
        )
        self.logger.info(f"Protocol version requested: {client_protocol}")

        # Use the client's protocol version if it's compatible, otherwise use ours
        protocol_version = (
            client_protocol if client_protocol.startswith("2025-") else self.protocol_version
        )

        return {
            "protocolVersion": protocol_version,
            "capabilities": {"tools": {"listChanged": True}, "resources": {"subscribe": False}},
            "serverInfo": self.server_info,
        }

    def handle_initialized(self, params: dict) -> dict:
        """Handle initialized notification from client.

        This is called after the client has processed the initialize response
        and is ready to start using the server.

        Args:
            params: Notification parameters (usually empty).

        Returns:
            Empty dict (this is a notification, no response needed).
        """
        self.logger.info("Client initialization complete - server ready for requests")
        return {}

    def handle_cancelled(self, params: dict) -> dict:
        """Handle operation cancellation notification.

        Args:
            params: Cancellation parameters.

        Returns:
            Empty dict (this is a notification).
        """
        self.logger.info("Operation cancelled by client")
        return {}

    def handle_list_tools(self, params: dict) -> dict:
        """Return list of available tools.

        Args:
            params: Parameters (unused for tool listing).

        Returns:
            Dictionary containing list of available tools with their schemas.
        """
        self.logger.debug("Listing available tools")

        tools_list = []
        for name, tool in self.tools.items():
            try:
                tools_list.append(
                    {
                        "name": name,
                        "description": tool.description,
                        "inputSchema": tool.get_input_schema(),
                    }
                )
            except Exception as e:
                self.logger.error(f"Error getting schema for tool {name}: {e}")

        return {"tools": tools_list}

    def handle_call_tool(self, params: dict) -> dict:
        """Execute a tool and return simplified HTML visualization results.

        Args:
            params: Tool execution parameters including tool name and arguments.

        Returns:
            Simplified tool execution results or error response.
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        self.logger.info(f"Executing tool: {tool_name}")

        if tool_name not in self.tools:
            return self.error_response(-32602, f"Unknown tool: {tool_name}")

        try:
            # Execute tool - gets statistical results
            result = self.tools[tool_name].execute(arguments)
            self.logger.debug(f"Tool {tool_name} executed successfully")

            # Create simplified visualization response
            from .utils.simplified_visualization import SimplifiedVisualizationResponse

            response_generator = SimplifiedVisualizationResponse(result, tool_name)
            enhanced_result = response_generator.generate_response()

            self.logger.info("Generated simplified response with HTML visualization")

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(enhanced_result, indent=2, cls=MCPJSONEncoder),
                    }
                ]
            }
        except ValueError as e:
            self.logger.error(f"Tool validation error for {tool_name}: {e}")
            return self.error_response(-32602, f"Invalid parameters: {str(e)}")
        except Exception as e:
            self.logger.error(f"Tool execution error for {tool_name}: {e}")
            return self.error_response(-32603, f"Tool execution failed: {str(e)}")

    def error_response(self, code: int, message: str) -> dict:
        """Create error response following JSON-RPC format.

        Args:
            code: Error code (following JSON-RPC error code conventions).
            message: Human-readable error message.

        Returns:
            Error response dictionary.
        """
        return {"error": {"code": code, "message": message}}

    def run(self) -> None:
        """Main server loop using stdio transport.

        Reads JSON-RPC requests from stdin and writes responses to stdout.
        Continues until EOF or error.
        """
        self.logger.info("ESTIEM EDA MCP Server started - listening on stdin")

        try:
            # Enable line buffering for stdin
            sys.stdin.reconfigure(line_buffering=True)

            while True:
                try:
                    # Read request from stdin - blocking read
                    line = sys.stdin.readline()

                    # Only break on true EOF (empty string), not on empty lines
                    if line == "":
                        self.logger.info("EOF received, shutting down server")
                        break

                    # Skip empty lines but continue processing
                    line = line.strip()
                    if not line:
                        continue

                    self.logger.debug(f"Raw input received: {line}")

                    # Parse JSON-RPC request
                    try:
                        request = json.loads(line)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON received: {e}")
                        continue

                    self.logger.debug(f"Received request: {request}")

                    # Handle request and get response
                    if "error" in request:
                        # This is an error response, not a request
                        self.logger.error(f"Received error from client: {request}")
                        continue

                    result = self.handle_request(request)

                    # Only send response if this is a request (has id), not a notification
                    if "id" in request:
                        # Create JSON-RPC response
                        response = {"jsonrpc": "2.0", "id": request.get("id")}

                        if "error" in result:
                            response["error"] = result["error"]
                        else:
                            response["result"] = result

                        # Send response to stdout
                        response_json = json.dumps(response)
                        sys.stdout.write(response_json + "\n")
                        sys.stdout.flush()

                        self.logger.debug(f"Sent response: {response}")
                    else:
                        self.logger.debug(f"Processed notification: {request.get('method')}")

                except KeyboardInterrupt:
                    self.logger.info("Keyboard interrupt received, shutting down")
                    break
                except Exception as e:
                    self.logger.error(f"Unexpected error in main loop: {e}")
                    # Continue running despite errors
                    continue
        except Exception as e:
            self.logger.error(f"Fatal server error: {e}")
        finally:
            self.logger.info("MCP Server shutting down")


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        server = ESTIEMMCPServer()
        server.run()
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
