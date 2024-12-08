import json

class ApiResponse:
    def __init__(self, message: str = None, error: str = None, response: str = "", statuscode: str = ""):

        # Ensure that either message or error is provided
        if message is None and error is None:
            raise ValueError("Either 'message' or 'error' must be provided.")
        elif message is not None and error is not None:
            raise ValueError("Both 'message' and 'error' cannot be set.")

        self.message = message
        self.error = error
        self.response = response
        self.statuscode = statuscode

    def to_dictionary(self) -> dict:

        """
        Convert the object to a dictionary, returning either
        message or error.
        """
        result = {
            "response": self.response,
            "status_code": self.statuscode
        }

        # Include either message or error in the JSON output
        if self.message is not None:
            result["message"] = self.message
        elif self.error is not None:
            result["error"] = self.error

        return result

    def __str__(self):
        """
            Return the JSON representation of the object when printed.
        """
        return json.dumps(self.to_dictionary())


# Example usage:
if __name__ == "__main__":

    # Example with a message
    api_response_success = ApiResponse(
        message="Operation successful",
        response="Here is your data",
        statuscode="200"
    )

    print(api_response_success)

    # Example with an error
    api_response_error = ApiResponse(
        error="An unexpected error occurred",
        response="",
        statuscode="500"
    )

    print(api_response_error)

    # Uncommenting the following line will raise a ValueError
    #api_response_invalid = ApiResponse("","")
