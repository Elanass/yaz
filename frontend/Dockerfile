# Base image
FROM nginx:alpine

# Copy static files
COPY static /usr/share/nginx/html

# Expose port
EXPOSE 80

# Command to run the application
CMD ["nginx", "-g", "daemon off;"]
