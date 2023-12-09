# hot-plugged-DNS
DNS Sinkhole Implementation in Python: A DNS sink server and JSON publisher that block specified domains and serve as a DNS sinkhole, redirecting queries to a local blacklist or Google DNS. Designed for testing and managing unwanted domain resolutions.

# DNS Sinkhole Implementation

This project offers a DNS sink server and a JSON publisher to manage and block specified domains. It functions as a DNS sinkhole, redirecting queries to a local blacklist or Google DNS, providing a robust solution for testing and managing unwanted domain resolutions.

## Features

- **DNS Sink Server:** Processes DNS queries, redirecting specified domains to a sinkhole IP address.
- **JSON Publisher:** Serves domain blacklists in compressed JSON format via HTTP.
- **Flexible Configuration:** Easily modify the list of blocked domains and customize settings.
- **Usage of Third-Party DNS:** Can query external DNS servers (e.g., Google's 8.8.8.8) for unresolved domains.

## Requirements

- Python 3.x
- Required libraries: `dnspython`, `colorama`, `requests`

## Usage

1. **Prepare DNS Blacklist:** Ensure `dns.blacklist` contains the list of blocked domains.
2. **Install Required Libraries:** 
    ```bash
    pip install dnspython colorama requests
    ```
3. **Generate Executables:** Create standalone executables using `pyinstaller` (for Windows):
    ```bash
    pyinstaller --onefile dnssinker.py
    pyinstaller --onefile http-dns-publisher.py
    ```
4. **Start JSON Publisher:** Serve the JSON data from the DNS blacklist:
    ```bash
    python3 http-dns-publisher.py
    ```
5. **Start DNS Sink Server:** Run the DNS sink server to process queries:
    ```bash
    python3 dnssinker.py
    ```
6. **Perform DNS Queries:** From a client machine, execute DNS queries:
    ```bash
    dig @<ip-addr-sink-server> -p 59 <domain-name>
    ```

## Contributing

Feel free to contribute by opening issues or creating pull requests.

## License

This project is licensed under the [MIT License](LICENSE).
