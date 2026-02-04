@echo off
REM run_all.cmd
start "payment-service" "C:\Program Files\Java\jdk-21\bin\java.exe" @"C:\Users\User\AppData\Local\Temp\cp_a7k6t2wqevnah0teu6pcfsu5r.argfile" com.paymentservice.paymentservice.PaymentServiceApplication
start "order-service"   "C:\Program Files\Java\jdk-21\bin\java.exe" @"C:\Users\User\AppData\Local\Temp\cp_d5244yo53ioxasfvohmc3dz92.argfile" com.orderservice.orderservice.OrderServiceApplication
cd /d inventory-service
start "inventory-service" uvicorn app.main:app --reload --port 8082
cd /d ..
cd /d notification-service
start "notification-service" uvicorn app.main:app --reload --port 8083

``