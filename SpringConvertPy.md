| Concept              | Spring                      | FastAPI                  |
| -------------------- | --------------------------- | ------------------------ |
| API endpoint         | `@GetMapping`               | `@app.get()`             |
| Request body         | DTO                         | Pydantic model           |
| Dependency Injection | `@Autowired`                | `Depends()`              |
| Service layer        | Service                     | service function         |
| Repository/DAO       | JPA Repository              | Mongo query / SQLAlchemy |
| Validation           | `@Valid`                    | Pydantic validation      |
| Async                | `CompletableFuture/WebFlux` | `async/await`            |
| Middleware           | Filter/Interceptor          | Middleware               |
| ORM                  | Hibernate                   | SQLAlchemy/Tortoise      |
| Config               | `application.yml`           | `.env/config.py`         |
