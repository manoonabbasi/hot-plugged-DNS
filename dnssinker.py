import dns.message
import dns.rcode
import socket
from colorama import Fore, Style
import requests
import time

def get_blocked_domains(url):
    # Fetches the blocked domains list from the provided URL
    response = requests.get(url)
    if response.status_code == 200:
        # Parses the response as JSON and removes trailing dots from domains
        blocked_domains = [domain.rstrip('.') for domain in response.json()]
        return blocked_domains
    else:
        # Returns an empty list if unable to fetch the domain list
        return []

def handle_query(data, sock, client_address, client_port, blocked_domains):
    # Processes incoming DNS queries
    request = dns.message.from_wire(data)
    requested_domain = str(request.question[0].name).rstrip('.')

    response = dns.message.make_response(request)
    response.question = request.question

    print(f"DNS Query received from: {client_address}:{client_port} for Domain '{requested_domain}'")

    if requested_domain in blocked_domains or requested_domain.rstrip('.') in blocked_domains:
        # Handles blocked domains by returning 0.0.0.0 as the response
        print(f"{Fore.RED}DNS sink activated, request forwarded to sink (0.0.0.0){Style.RESET_ALL}")
        response.set_rcode(dns.rcode.NXDOMAIN)

        # Prepares the response with a blank IP address
        rr_type = dns.rdatatype.A
        ttl = 300
        rdata = "0.0.0.0"
        # Constructs the DNS response
        rrset = dns.rdataset.from_text(dns.rdataclass.IN, rr_type, ttl)
        rrset.add(dns.rdata.from_text(dns.rdataclass.IN, rr_type, rdata, ttl))
        name = dns.name.from_text(requested_domain)
        response.answer.append(dns.rrset.RRset(name, dns.rdataclass.IN, rr_type, ttl))
        response.answer[0].add(dns.rdata.from_text(dns.rdataclass.IN, rr_type, rdata))
    else:
        try:
            # Forwards queries to Google's DNS server if the domain is not blocked
            google_dns = ("8.8.8.8", 53)
            google_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            google_sock.sendto(data, google_dns)
            google_sock.settimeout(5)  # Timeout for receiving response from Google's DNS server
            google_response_data, _ = google_sock.recvfrom(1024)
            google_response = dns.message.from_wire(google_response_data)

            # Displays the response from Google's DNS server
            print(f"Received response from Google DNS for '{requested_domain}':")
            print(google_response)

            # Sends the Google DNS response back to the client
            sock.sendto(google_response_data, (client_address, client_port))
        except socket.timeout:
            # Handles scenarios where the domain is not found in the blocked list or Google's DNS
            print(f"Domain '{requested_domain}' not found in blocked list. Processing with external DNS Server (Default: 8.8.8.8)")

            # Prepares a response with a blank IP address (0.0.0.0)
            response.set_rcode(dns.rcode.NOERROR)
            rr_type = dns.rdatatype.A
            ttl = 300
            rdata = "0.0.0.0"
            rrset = dns.rdataset.from_text(dns.rdataclass.IN, rr_type, ttl)
            rrset.add(dns.rdata.from_text(dns.rdataclass.IN, rr_type, rdata, ttl))
            name = dns.name.from_text(requested_domain)
            response.answer.append(dns.rrset.RRset(name, dns.rdataclass.IN, rr_type, ttl))
            response.answer[0].add(dns.rdata.from_text(dns.rdataclass.IN, rr_type, rdata))

    # Sends the DNS response back to the client
    response_data = response.to_wire()
    response_data += b'\x00' * (512 - len(response_data))
    sock.sendto(response_data, (client_address, client_port))

def main():
    # Defines the URL for fetching the blocked domains list
    blocked_domains_url = "http://127.0.0.1:7000/v1/API.json"

    # Configures the socket for DNS queries
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 59))
    # Change the port here, put 53 instead of 59 if want to simulate for any specific services
    
    last_fetch_time = 0
    blocked_domains = []

    while True:
        # Fetches the updated blocked domains list every 60 seconds
        current_time = time.time()
        if current_time - last_fetch_time >= 60:
            blocked_domains = get_blocked_domains(blocked_domains_url)
            last_fetch_time = current_time

        try:
            # Listens for incoming DNS queries and handles them
            data, (client_address, client_port) = sock.recvfrom(1024)
            handle_query(data, sock, client_address, client_port, blocked_domains)
        except Exception as e:
            # Handles any exceptions that occur during the process
            print("An error occurred:", e)

if __name__ == "__main__":
    main()
