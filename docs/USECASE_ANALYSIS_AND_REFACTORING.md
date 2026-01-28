# Use Case 역할 분석 및 리팩토링 가이드

## 📋 목차
1. [Use Case의 정의](#1-use-case의-정의)
2. [현재 프로젝트의 UseCase 분석](#2-현재-프로젝트의-usecase-분석)
3. [문제점 진단](#3-문제점-진단)
4. [올바른 Use Case 설계](#4-올바른-use-case-설계)
5. [구체적인 리팩토링 방안](#5-구체적인-리팩토링-방안)
6. [실전 체크리스트](#6-실전-체크리스트)

---

## 1. Use Case의 정의

### 📌 One-liner 정의

> **Use Case는 "사용자가 시스템을 통해 달성하고자 하는 하나의 완전한 비즈니스 목표"를 구현하는 애플리케이션 계층의 오케스트레이터다.**

### 왜 존재하는가?

Use Case는 **"비즈니스 시나리오의 실행 단위"**다.

- ❌ 데이터를 가져오기 위해 존재하는 게 아니다
- ❌ Service와 Repository 사이의 중간 계층이 아니다
- ✅ **"회원가입", "로그인", "주문하기"** 같은 **완전한 비즈니스 흐름**을 구현한다

### 무엇을 책임지는가?

```
Use Case의 책임 = 시나리오 오케스트레이션 + 트랜잭션 경계 + 비즈니스 규칙 실행
```

**구체적으로:**

1. **비즈니스 시나리오 구현**
   - "사용자가 회원가입한다" → 중복 검증 → 비밀번호 암호화 → DB 저장 → 환영 이메일 발송
   - "사용자가 로그인한다" → 인증 → 토큰 생성 → Redis 캐싱 → 로그인 이력 저장

2. **도메인 객체 조율**
   - 여러 Entity/Service를 조합하여 비즈니스 목표 달성
   - 도메인 규칙 검증 및 실행

3. **트랜잭션 경계 정의**
   - 하나의 Use Case = 하나의 트랜잭션 단위 (원칙적으로)
   - ACID 보장이 필요한 범위 결정

4. **애플리케이션 흐름 제어**
   - if/else 분기, 예외 처리, 보상 트랜잭션
   - 하지만 **도메인 로직 자체는 Domain Layer에 위임**

### 무엇을 절대 하면 안 되는가?

| ❌ 금지 사항 | 이유 |
|------------|------|
| **Infrastructure 직접 접근** | Redis, 외부 API 등은 Repository/Adapter를 통해 접근 |
| **HTTP 요청/응답 객체 의존** | Use Case는 프레임워크에 독립적이어야 함 |
| **단순 CRUD 래퍼** | Repository를 그대로 호출만 하는 건 Use Case가 아님 |
| **복잡한 도메인 로직 구현** | 도메인 규칙은 Entity/Domain Service에 위임 |
| **Presentation 관심사 처리** | JSON 변환, HTTP 상태 코드 등은 Controller/Facade 책임 |

---

## 2. 현재 프로젝트의 UseCase 분석

### 🔍 현재 구조

```
Endpoint → Facade → Service → UseCase → Repository → DB
                              ↓
                            Redis (직접 접근!)
```

### 📂 현재 UseCase 코드

```python
# src/app/auth/usecase/user_usecase.py
class UserUseCase:
    @inject
    async def get_one(
        self,
        user_repository: UserRepository = Provide["auth.user_repository"],
        **kwargs,
    ) -> UserEntity | None:
        where = []
        if kwargs.get("user_id"):
            where.append(UserInfo.user_id == kwargs["user_id"])
        if kwargs.get("login_id"):
            where.append(UserInfo.login_id == kwargs["login_id"])

        user_entity = await user_repository.one(*where)
        if not user_entity:
            raise errors.NotFoundUserEx()
        return user_entity

    @inject
    async def set_user_in_redis(
        self,
        user_entity: UserEntity,
        redis=Provide["redis"],  # ⚠️ Infrastructure 직접 의존
        config=Provide["config"],
    ) -> None:
        await redis.set(
            name=f"cahce_user_info_{user_entity.login_id}",
            value=str({...}),
            ex=config["REDIS_EXPIRE_TIME"],
        )
```

### 🎭 현재 UseCase의 실제 역할

현재 `UserUseCase`는:

1. **Repository 호출의 얇은 래퍼** 역할
   - `get_one()` → Repository의 `one()` 호출만 함
   - Where 절 조건 구성 로직만 추가

2. **Infrastructure(Redis) 직접 조작**
   - `set_user_in_redis()`에서 Redis를 직접 호출
   - 캐싱은 Infrastructure 관심사인데 Application Layer에서 처리

3. **비즈니스 시나리오가 아닌 단순 CRUD**
   - "사용자 조회", "Redis 저장" 같은 기술적 작업
   - **"회원가입", "로그인"** 같은 비즈니스 시나리오가 없음

### 📊 현재 흐름 예시: 로그인

```python
# endpoint/login.py
@router.post("/login")
async def login(form_data, auth_facade: AuthFacade = Depends()):
    return await auth_facade.login(request, username, password)

# facades/auth_facade.py
async def login(self, request, username, password):
    # 1. 인증
    authenticated_user = await self.auth_service.authenticate(username, password)
    # 2. 토큰 생성
    user_with_token = await self.token_service.get_token(request, authenticated_user)
    # 3. Redis 캐싱
    await self.user_service.save_user_in_redis(user_with_token)
    # 4. 응답 생성
    return response

# services/user_service.py
async def save_user_in_redis(self, user_entity):
    await self.user_usecase.set_user_in_redis(user_entity)

# usecase/user_usecase.py
async def set_user_in_redis(self, user_entity, redis=Provide["redis"]):
    await redis.set(...)  # Redis 직접 호출
```

**문제점:**
- **Facade가 실제 Use Case 역할을 수행** (시나리오 오케스트레이션)
- UseCase는 단순 Redis 호출 래퍼로 전락
- 계층 간 책임이 뒤섞임

---

## 3. 문제점 진단

### 🚨 핵심 문제

#### 문제 1: Use Case가 "Repository의 얇은 래퍼"로 전락

```python
# ❌ 잘못된 예시 - 현재 코드
class UserUseCase:
    async def get_one(self, user_repository, **kwargs):
        where = [...]
        user = await user_repository.one(*where)
        if not user:
            raise NotFoundUserEx()
        return user
```

**왜 문제인가?**
- Repository 메서드를 거의 그대로 호출만 함
- 비즈니스 로직이 전혀 없음
- Where 절 조건 구성은 Repository의 책임이어야 함
- **이건 Use Case가 아니라 Repository 패턴의 일부다**

#### 문제 2: Infrastructure(Redis) 직접 의존

```python
# ❌ 잘못된 예시
async def set_user_in_redis(self, user_entity, redis=Provide["redis"]):
    await redis.set(...)  # Infrastructure 직접 접근
```

**왜 문제인가?**
- Use Case가 Redis라는 구체적인 기술에 의존
- 나중에 Memcached로 변경하려면 Use Case 코드 수정 필요
- **의존성 역전 원칙(DIP) 위반**
- 캐싱은 Repository/Adapter 계층에서 처리해야 함

#### 문제 3: 비즈니스 시나리오가 Facade에 구현됨

```python
# ❌ 잘못된 예시 - Facade가 Use Case 역할 수행
class AuthFacade:
    async def login(self, request, username, password):
        authenticated_user = await self.auth_service.authenticate(...)
        user_with_token = await self.token_service.get_token(...)
        await self.user_service.save_user_in_redis(...)
        return response
```

**왜 문제인가?**
- **"로그인"이라는 비즈니스 시나리오가 Facade에 구현됨**
- Facade는 Presentation Layer의 책임 (응답 변환, HTTP 처리)
- 이 로직을 테스트하려면 FastAPI 의존성 필요 → 단위 테스트 어려움
- **비즈니스 로직이 프레임워크에 종속됨**

#### 문제 4: Service 계층의 모호한 역할

```python
# ❌ 현재 구조
class UserService:
    async def register(self, request):
        entity = UserEntity.from_dict(request.dict())
        deleted_none = entity.delete_to_dict_none_data()
        return await self.user_usecase.user_insert(deleted_none)
```

**왜 문제인가?**
- Service가 단순 DTO 변환 + UseCase 호출만 함
- Service의 존재 이유가 불명확
- UseCase와 Service의 경계가 모호

---

### 🎯 초보자가 가장 많이 하는 오해 Top 3

#### 오해 1: "Use Case = Repository 위의 얇은 레이어"

```python
# ❌ 잘못된 생각
class UserUseCase:
    async def get_user_by_id(self, user_id):
        return await self.repository.find_by_id(user_id)
```

**진실:**
- 이건 Use Case가 아니라 Repository 메서드의 alias일 뿐
- Use Case는 **완전한 비즈니스 시나리오**를 구현해야 함
- 단순 조회/저장은 Repository로 충분

#### 오해 2: "모든 비즈니스 로직은 Use Case에"

```python
# ❌ 잘못된 생각
class RegisterUserUseCase:
    async def execute(self, email, password):
        # 이메일 검증 로직 (도메인 규칙)
        if not "@" in email:
            raise InvalidEmail()
        # 비밀번호 강도 검증 (도메인 규칙)
        if len(password) < 8:
            raise WeakPassword()
        ...
```

**진실:**
- **도메인 규칙은 Entity/Value Object/Domain Service에**
- Use Case는 도메인 객체를 **조율**하는 역할
- "이메일이 유효한가"는 Email VO의 책임
- "비밀번호가 강한가"는 Password VO의 책임

#### 오해 3: "Use Case는 Controller/Facade와 비슷한 것"

```python
# ❌ 잘못된 생각
class LoginUseCase:
    async def execute(self, request: Request, response: Response):
        # HTTP 관심사를 Use Case에...
        user = await self.authenticate(request.form_data)
        response.set_cookie("token", user.token)
        return JSONResponse(...)
```

**진실:**
- Use Case는 **프레임워크에 독립적**이어야 함
- HTTP Request/Response를 직접 다루면 안 됨
- 입력은 DTO/Command, 출력도 순수한 도메인 객체/DTO

---

## 4. 올바른 Use Case 설계

### ✅ Use Case가 다루는 것

| 항목 | 설명 | 예시 |
|-----|------|------|
| **비즈니스 시나리오 구현** | 완전한 사용자 목표 달성 | "회원가입", "로그인", "주문 결제" |
| **도메인 객체 조율** | Entity, VO, Domain Service 조합 | User 생성 + 이메일 검증 + 알림 발송 |
| **트랜잭션 경계** | ACID가 필요한 범위 정의 | 주문 생성 + 재고 감소 + 포인트 차감 |
| **애플리케이션 규칙** | 도메인 규칙이 아닌 워크플로우 제어 | "관리자만 접근 가능" 같은 권한 검증 |
| **외부 서비스 조율** | Repository/Adapter를 통한 간접 호출 | 이메일 발송, 결제 API 호출 |

### ❌ Use Case가 다루지 않는 것

| 항목 | 이유 | 대신 누가? |
|-----|------|----------|
| **HTTP 요청/응답** | 프레임워크 종속 | Controller/Endpoint |
| **데이터베이스 쿼리** | Infrastructure 관심사 | Repository |
| **JSON 직렬화** | Presentation 관심사 | Serializer/Facade |
| **도메인 규칙 검증** | 도메인 로직 | Entity/VO/Domain Service |
| **캐싱 전략** | Infrastructure 관심사 | Repository/Cache Adapter |

### 🔄 Service vs Use Case 경계 기준

#### Service (Domain Service)

```python
# ✅ Domain Service - 도메인 규칙 구현
class AuthenticationService:
    """도메인 로직: "이 사용자가 인증되었는가?"라는 도메인 질문에 답함"""
    async def verify_password(self, plain: str, hashed: str) -> bool:
        return self.pwd_context.verify(plain, hashed)

    async def authenticate(self, login_id: str, password: str) -> User:
        user = await self.user_repo.find_by_login_id(login_id)
        if not user or not self.verify_password(password, user.password):
            raise AuthenticationFailed()
        return user
```

**특징:**
- **도메인 개념**을 다룸 ("인증", "권한", "주문")
- 여러 Entity를 조합한 **도메인 로직**
- 상태가 없거나 도메인 상태만 가짐
- Use Case에서 호출됨

#### Use Case (Application Service)

```python
# ✅ Use Case - 비즈니스 시나리오 구현
class LoginUseCase:
    """애플리케이션 시나리오: "사용자가 로그인한다"는 완전한 흐름"""
    def __init__(
        self,
        auth_service: AuthenticationService,  # Domain Service
        token_service: TokenService,          # Domain Service
        user_repo: UserRepository,
        cache_repo: CacheRepository
    ):
        ...

    async def execute(self, command: LoginCommand) -> LoginResult:
        # 1. 도메인 서비스로 인증
        user = await self.auth_service.authenticate(
            command.login_id,
            command.password
        )

        # 2. 도메인 서비스로 토큰 생성
        tokens = self.token_service.create_tokens(user)

        # 3. Repository로 캐싱 (Infrastructure 추상화)
        await self.cache_repo.set_user_session(user, tokens)

        # 4. 결과 반환 (순수한 도메인 객체/DTO)
        return LoginResult(
            user_id=user.id,
            login_id=user.login_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token
        )
```

**특징:**
- **사용자 시나리오** 구현 ("로그인", "회원가입")
- Domain Service를 **조율**
- Infrastructure는 **Repository/Adapter를 통해 간접 접근**
- 입력은 Command/DTO, 출력도 DTO

### 📊 경계 판단 표

| 질문 | Domain Service | Use Case |
|-----|---------------|----------|
| "이 로직이 다른 Use Case에서도 쓰이나?" | ✅ | ❌ |
| "도메인 개념을 표현하는가?" | ✅ | ❌ |
| "사용자 시나리오를 표현하는가?" | ❌ | ✅ |
| "여러 서비스를 조합하는가?" | 때때로 | ✅ 항상 |
| "트랜잭션 경계를 정의하는가?" | ❌ | ✅ |

---

### 🔐 트랜잭션과 Use Case의 관계

#### 원칙

> **하나의 Use Case = 하나의 트랜잭션 단위** (원칙적으로)

**왜?**
- Use Case는 **완전한 비즈니스 동작**을 표현
- 비즈니스 동작은 **원자적(Atomic)** 이어야 함
- 중간에 실패하면 전체 롤백되어야 일관성 유지

#### 예시

```python
# ✅ 올바른 트랜잭션 경계
class RegisterUserUseCase:
    @transactional  # 전체가 하나의 트랜잭션
    async def execute(self, command: RegisterCommand) -> User:
        # 1. 중복 검증
        if await self.user_repo.exists_by_email(command.email):
            raise DuplicateUserError()

        # 2. 사용자 생성 (도메인 로직은 Entity에)
        user = User.create(
            email=Email(command.email),
            password=Password(command.password),
            name=command.name
        )

        # 3. DB 저장
        await self.user_repo.save(user)

        # 4. 환영 이메일 발송 (비동기로 처리하거나 이벤트로 분리)
        await self.email_service.send_welcome_email(user.email)

        return user
```

**트랜잭션 경계 설정 시 고려사항:**

1. **외부 API 호출은 트랜잭션 밖으로**
   - 결제 API, 이메일 발송 등은 롤백 불가능
   - Saga Pattern이나 Eventual Consistency 고려

2. **긴 작업은 분리**
   - 이미지 처리, 대량 데이터 조회 등
   - 별도 Use Case나 비동기 작업으로 분리

3. **읽기 전용은 트랜잭션 불필요**
   - 조회 Use Case는 `@transactional(readonly=true)`

---

### 📋 "Use Case를 만들어야 하는 신호" 체크리스트

다음 중 **2개 이상** 해당하면 Use Case를 만들어라:

- [ ] **여러 Repository/Service를 조합**해야 한다
- [ ] **트랜잭션 경계**가 필요하다
- [ ] **비즈니스 규칙 검증**이 필요하다 (도메인 규칙 제외)
- [ ] **외부 시스템과 연동**해야 한다
- [ ] 이 로직을 **독립적으로 테스트**하고 싶다
- [ ] **사용자의 의도/목표**를 표현하는 동작이다
- [ ] **if/else 분기가 복잡**하고 비즈니스 흐름을 제어한다
- [ ] Facade/Controller가 **3개 이상의 서비스를 호출**한다

#### 예시

| 시나리오 | Use Case 필요? | 이유 |
|---------|---------------|------|
| "사용자 ID로 조회" | ❌ | Repository로 충분 |
| "로그인" | ✅ | 인증 + 토큰 생성 + 캐싱 조합 |
| "회원가입" | ✅ | 중복 검증 + 생성 + 환영 메일 |
| "비밀번호 변경" | ✅ | 인증 + 검증 + 업데이트 + 알림 |
| "사용자 목록 조회" | ❌ | 단순 조회, Repository로 충분 |
| "주문 결제" | ✅✅ | 재고 확인 + 결제 + 재고 감소 + 알림 (복잡한 시나리오) |

---

## 5. 구체적인 리팩토링 방안

### 🎯 목표 구조

```
Endpoint → Use Case → Domain Service → Repository → DB
                     ↓
                   Cache Repository (추상화)
```

**핵심 변화:**
1. Facade 제거 또는 단순 DTO 변환만 담당
2. 비즈니스 시나리오는 Use Case로 이동
3. Infrastructure 직접 접근 제거 → Repository/Adapter로 추상화

---

### 📝 리팩토링 예시 1: Login Use Case

#### Before (현재)

```python
# endpoint/login.py
@router.post("/login")
async def login(form_data, auth_facade: AuthFacade = Depends()):
    return await auth_facade.login(request, username, password)

# facades/auth_facade.py
class AuthFacade:
    async def login(self, request, username, password):
        authenticated_user = await self.auth_service.authenticate(username, password)
        user_with_token = await self.token_service.get_token(request, authenticated_user)
        await self.user_service.save_user_in_redis(user_with_token)
        response = ResponsJson.extract_response_fields(...)
        response.set_cookie("access_token", ...)
        return response

# usecase/user_usecase.py
class UserUseCase:
    async def set_user_in_redis(self, user_entity, redis=Provide["redis"]):
        await redis.set(...)  # Redis 직접 접근
```

**문제점:**
- 비즈니스 로직이 Facade에 있음 (프레임워크 종속)
- UseCase가 Redis 직접 접근 (Infrastructure 의존)
- HTTP 관심사(cookie)와 비즈니스 로직 혼재

#### After (개선)

```python
# ========================================
# 1. Command/Result DTO 정의
# ========================================
# app/auth/usecases/dto.py
from dataclasses import dataclass

@dataclass(frozen=True)
class LoginCommand:
    """Use Case 입력 - 프레임워크 독립적"""
    login_id: str
    password: str

@dataclass(frozen=True)
class LoginResult:
    """Use Case 출력 - 프레임워크 독립적"""
    user_id: int
    login_id: str
    user_name: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# ========================================
# 2. Repository 인터페이스 (추상화)
# ========================================
# app/auth/repositories/cache_repository.py
from abc import ABC, abstractmethod
from app.auth.domain.user_entity import UserEntity

class CacheRepository(ABC):
    """캐시 저장소 추상화 - Infrastructure 구체 기술 숨김"""

    @abstractmethod
    async def set_user_session(
        self,
        user: UserEntity,
        access_token: str,
        refresh_token: str,
        ttl_seconds: int
    ) -> None:
        pass

    @abstractmethod
    async def get_user_session(self, login_id: str) -> UserEntity | None:
        pass

# ========================================
# 3. Redis 구현체 (Infrastructure Layer)
# ========================================
# infrastructure/cache/redis_cache_repository.py
class RedisCacheRepository(CacheRepository):
    def __init__(self, redis_client, config):
        self.redis = redis_client
        self.config = config

    async def set_user_session(
        self,
        user: UserEntity,
        access_token: str,
        refresh_token: str,
        ttl_seconds: int
    ) -> None:
        await self.redis.set(
            name=f"cache_user_info_{user.login_id}",  # 오타 수정
            value=json.dumps({
                "user_id": user.user_id,
                "login_id": user.login_id,
                "user_name": user.user_name,
                "user_type": user.user_type,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }),
            ex=ttl_seconds
        )

    async def get_user_session(self, login_id: str) -> UserEntity | None:
        data = await self.redis.get(f"cache_user_info_{login_id}")
        if not data:
            return None
        return UserEntity.from_dict(json.loads(data))

# ========================================
# 4. Use Case 구현 (핵심!)
# ========================================
# app/auth/usecases/login_usecase.py
class LoginUseCase:
    """
    Use Case: 사용자 로그인

    책임:
    - 사용자 인증 시나리오 오케스트레이션
    - 토큰 생성 및 세션 캐싱
    - 트랜잭션 경계 관리
    """

    def __init__(
        self,
        auth_service: AuthenticationService,  # Domain Service
        token_service: TokenService,          # Domain Service
        cache_repository: CacheRepository,    # Infrastructure 추상화
        config: Config
    ):
        self.auth_service = auth_service
        self.token_service = token_service
        self.cache_repo = cache_repository
        self.config = config

    async def execute(self, command: LoginCommand) -> LoginResult:
        """
        로그인 Use Case 실행

        Args:
            command: 로그인 명령 (login_id, password)

        Returns:
            LoginResult: 로그인 결과 (user 정보 + 토큰)

        Raises:
            NotFoundUserEx: 사용자가 존재하지 않음
            BadPassword: 비밀번호 불일치
        """

        # 1. 도메인 서비스로 사용자 인증
        user = await self.auth_service.authenticate(
            user_id=command.login_id,
            user_passwd=command.password
        )
        # auth_service.authenticate()는 이미 예외를 던지므로
        # 여기서는 성공한 user만 받음

        # 2. 도메인 서비스로 토큰 생성
        tokens = self.token_service.create_tokens(
            user_id=user.user_id,
            login_id=user.login_id,
            user_name=user.user_name,
            user_type=user.user_type
        )

        # 3. 캐시에 세션 저장 (Repository 추상화 사용)
        await self.cache_repo.set_user_session(
            user=user,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            ttl_seconds=self.config.REDIS_EXPIRE_TIME
        )

        # 4. Use Case 결과 반환 (순수한 DTO)
        return LoginResult(
            user_id=user.user_id,
            login_id=user.login_id,
            user_name=user.user_name,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer"
        )

# ========================================
# 5. TokenService 리팩토링
# ========================================
# app/auth/services/token_service.py
from dataclasses import dataclass

@dataclass
class Tokens:
    access_token: str
    refresh_token: str

class TokenService:
    """도메인 서비스: 토큰 생성 로직"""

    def __init__(self, config: Config):
        self.config = config

    def create_tokens(
        self,
        user_id: int,
        login_id: str,
        user_name: str,
        user_type: int
    ) -> Tokens:
        """
        JWT 토큰 생성 (access + refresh)

        Note: HTTP Request 객체 의존 제거!
        """
        access_token = create_access_token(
            jwt_secret_key=self.config.JWT_ACCESS_SECRET_KEY,
            jwt_algorithm=self.config.JWT_ALGORITHM,
            user_id=user_id,
            login_id=login_id,
            user_name=user_name,
            user_type=user_type,
            expire=self.config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        refresh_token = create_access_token(
            jwt_secret_key=self.config.JWT_REFRESH_SECRET_KEY,
            jwt_algorithm=self.config.JWT_ALGORITHM,
            user_id=user_id,
            login_id=login_id,
            user_name=user_name,
            user_type=user_type,
            expire=self.config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        )

        return Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )

# ========================================
# 6. Endpoint (단순화)
# ========================================
# app/auth/endpoint/login.py
@router.post("/login", response_model=ResponseLoginModel)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    login_usecase: LoginUseCase = Depends()  # Use Case 주입
):
    """
    로그인 엔드포인트

    책임:
    - HTTP 요청 파싱
    - Use Case 호출
    - HTTP 응답 생성 (쿠키 설정 등)
    """

    # 1. HTTP 입력 → Command 변환
    command = LoginCommand(
        login_id=form_data.username,
        password=form_data.password
    )

    # 2. Use Case 실행 (비즈니스 로직)
    result = await login_usecase.execute(command)

    # 3. Use Case 결과 → HTTP 응답 변환
    response = JSONResponse(content={
        "user_id": result.user_id,
        "login_id": result.login_id,
        "user_name": result.user_name,
        "access_token": result.access_token,
        "refresh_token": result.refresh_token,
        "token_type": result.token_type
    })

    # 4. HTTP 관심사 처리 (쿠키 설정)
    response.set_cookie(
        "access_token",
        result.access_token,
        httponly=True,
        secure=True,
        samesite="strict"
    )
    response.set_cookie(
        "refresh_token",
        result.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict"
    )

    return response
```

**개선 효과:**

✅ **Use Case가 비즈니스 시나리오 구현**
- "로그인"이라는 완전한 흐름을 Use Case에서 처리
- 인증 → 토큰 생성 → 캐싱 오케스트레이션

✅ **프레임워크 독립성**
- Use Case는 HTTP Request/Response를 모름
- Command/Result DTO로 입출력
- FastAPI를 Spring으로 바꿔도 Use Case 코드 변경 없음

✅ **Infrastructure 추상화**
- Redis 직접 의존 제거
- CacheRepository 인터페이스로 추상화
- 나중에 Memcached로 교체해도 Use Case 코드 불변

✅ **테스트 용이성**
```python
# 단위 테스트 예시
async def test_login_success():
    # Mock 객체로 쉽게 테스트
    mock_auth = Mock(AuthenticationService)
    mock_token = Mock(TokenService)
    mock_cache = Mock(CacheRepository)

    usecase = LoginUseCase(mock_auth, mock_token, mock_cache, config)

    command = LoginCommand(login_id="test", password="test123")
    result = await usecase.execute(command)

    assert result.login_id == "test"
    assert result.access_token is not None
```

---

### 📝 리팩토링 예시 2: Register Use Case

#### Before

```python
# endpoint/register.py
@router.post("/register")
async def register(request: RequestRegisterModel, auth_facade: AuthFacade = Depends()):
    return await auth_facade.register(request)

# facades/auth_facade.py
async def register(self, request: RequestRegisterModel):
    if await self.user_service.register(request):
        return JSONResponse(content={"status": 200, "msg": "Success Register."})

# services/user_service.py
async def register(self, request_user_info: RequestRegisterModel) -> bool:
    request_entity = UserEntity.from_dict(request_user_info.dict())
    deleted_none_data = request_entity.delete_to_dict_none_data()
    return await self.user_usecase.user_insert(deleted_none_data)

# usecase/user_usecase.py
async def user_insert(self, insert_user_entity: dict, user_repository) -> bool:
    return await user_repository.insert_user(insert_user_entity)
```

**문제점:**
- UseCase가 Repository 메서드 그대로 호출만 함
- 중복 검증 로직이 없음
- 비밀번호 해싱이 어디서 일어나는지 불명확
- dict로 데이터 전달 (타입 안전성 없음)

#### After

```python
# ========================================
# 1. Command/Result DTO
# ========================================
@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    login_id: str
    password: str  # 평문 비밀번호
    user_name: str

@dataclass(frozen=True)
class RegisterUserResult:
    user_id: int
    login_id: str
    email: str
    user_name: str

# ========================================
# 2. Use Case 구현
# ========================================
class RegisterUserUseCase:
    """
    Use Case: 사용자 회원가입

    책임:
    - 중복 검증
    - 사용자 생성 및 저장
    - 환영 이메일 발송 (선택)
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,  # Domain Service
        email_service: EmailService | None = None  # Optional
    ):
        self.user_repo = user_repository
        self.password_service = password_service
        self.email_service = email_service

    async def execute(self, command: RegisterUserCommand) -> RegisterUserResult:
        """
        회원가입 Use Case 실행

        Args:
            command: 회원가입 정보

        Returns:
            RegisterUserResult: 생성된 사용자 정보

        Raises:
            DuplicateUserEx: 이미 존재하는 login_id 또는 email
            InvalidEmailEx: 유효하지 않은 이메일
            WeakPasswordEx: 약한 비밀번호
        """

        # 1. 중복 검증 (Application 규칙)
        if await self.user_repo.exists_by_login_id(command.login_id):
            raise DuplicateUserEx(user_id=command.login_id)

        if await self.user_repo.exists_by_email(command.email):
            raise DuplicateUserEx(user_id=command.email)

        # 2. 도메인 객체 생성 (도메인 규칙은 Entity에서)
        # Email, Password는 Value Object로 검증 포함
        user = UserEntity.create(
            login_id=command.login_id,
            email=Email(command.email),  # VO가 유효성 검증
            password=Password.from_plain(command.password),  # VO가 강도 검증
            user_name=command.user_name
        )

        # 3. 비밀번호 해싱 (Domain Service)
        hashed_password = self.password_service.hash_password(
            user.password.value
        )
        user.password = Password.from_hashed(hashed_password)

        # 4. Repository로 저장
        saved_user = await self.user_repo.save(user)

        # 5. 환영 이메일 발송 (선택적, 비동기)
        if self.email_service:
            # 실패해도 회원가입은 성공으로 처리
            try:
                await self.email_service.send_welcome_email(
                    to_email=saved_user.email.value,
                    user_name=saved_user.user_name
                )
            except Exception as e:
                # 로깅만 하고 무시 (또는 이벤트로 재처리)
                logger.warning(f"Failed to send welcome email: {e}")

        # 6. 결과 반환
        return RegisterUserResult(
            user_id=saved_user.user_id,
            login_id=saved_user.login_id,
            email=saved_user.email.value,
            user_name=saved_user.user_name
        )

# ========================================
# 3. Repository에 중복 검증 메서드 추가
# ========================================
class UserRepository:
    async def exists_by_login_id(self, login_id: str) -> bool:
        async with self.session_factory() as session:
            result = await session.scalar(
                select(exists().where(UserInfo.login_id == login_id))
            )
            return result or False

    async def exists_by_email(self, email: str) -> bool:
        async with self.session_factory() as session:
            result = await session.scalar(
                select(exists().where(UserInfo.email == email))
            )
            return result or False

    async def save(self, user: UserEntity) -> UserEntity:
        """
        사용자 저장 (생성 또는 업데이트)

        Returns:
            저장된 UserEntity (user_id 포함)
        """
        async with self.session_factory() as session:
            if user.user_id:
                # 업데이트
                stmt = (
                    update(UserInfo)
                    .where(UserInfo.user_id == user.user_id)
                    .values(**user.to_dict())
                )
                await session.execute(stmt)
            else:
                # 생성
                stmt = insert(UserInfo).values(**user.to_dict()).returning(UserInfo)
                result = await session.execute(stmt)
                user_info = result.fetchone()
                user.user_id = user_info.user_id

            return user

# ========================================
# 4. Domain Entity 개선
# ========================================
@dataclass
class UserEntity:
    user_id: int | None
    login_id: str
    email: Email  # Value Object
    password: Password  # Value Object
    user_name: str
    user_type: int = 0

    @staticmethod
    def create(
        login_id: str,
        email: Email,
        password: Password,
        user_name: str
    ) -> "UserEntity":
        """
        팩토리 메서드: 새 사용자 생성

        도메인 규칙:
        - login_id는 공백 불가
        - user_name은 2자 이상
        """
        if not login_id or not login_id.strip():
            raise InvalidLoginId("Login ID cannot be empty")

        if not user_name or len(user_name.strip()) < 2:
            raise InvalidUserName("User name must be at least 2 characters")

        return UserEntity(
            user_id=None,  # 아직 저장 전
            login_id=login_id.strip(),
            email=email,
            password=password,
            user_name=user_name.strip(),
            user_type=0
        )

# ========================================
# 5. Value Object 예시
# ========================================
@dataclass(frozen=True)
class Email:
    """Email Value Object - 이메일 유효성 검증"""
    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise InvalidEmailEx(f"Invalid email format: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        import re
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

@dataclass(frozen=True)
class Password:
    """Password Value Object - 비밀번호 강도 검증"""
    value: str
    is_hashed: bool = False

    def __post_init__(self):
        if not self.is_hashed and not self._is_strong(self.value):
            raise WeakPasswordEx(
                "Password must be at least 8 characters with letters and numbers"
            )

    @staticmethod
    def from_plain(plain: str) -> "Password":
        return Password(value=plain, is_hashed=False)

    @staticmethod
    def from_hashed(hashed: str) -> "Password":
        return Password(value=hashed, is_hashed=True)

    @staticmethod
    def _is_strong(password: str) -> bool:
        if len(password) < 8:
            return False
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        return has_letter and has_number

# ========================================
# 6. Endpoint (단순화)
# ========================================
@router.post("/register")
async def register(
    request: RequestRegisterModel,
    register_usecase: RegisterUserUseCase = Depends()
):
    """
    회원가입 엔드포인트

    책임: HTTP 요청/응답 처리만
    """

    # 1. HTTP 입력 → Command 변환
    command = RegisterUserCommand(
        email=request.user_email,
        login_id=request.login_id,
        password=request.user_password,
        user_name=request.user_name
    )

    # 2. Use Case 실행
    result = await register_usecase.execute(command)

    # 3. HTTP 응답 생성
    return JSONResponse(content={
        "status": 200,
        "msg": "Success Register.",
        "data": {
            "user_id": result.user_id,
            "login_id": result.login_id
        }
    })
```

**개선 효과:**

✅ **비즈니스 규칙이 명확한 위치에**
- 이메일 검증 → `Email` VO
- 비밀번호 강도 → `Password` VO
- 중복 검증 → Use Case (Application 규칙)
- 사용자 생성 규칙 → `UserEntity.create()` (Domain 규칙)

✅ **Use Case가 실제 시나리오 구현**
- 중복 검증 → 생성 → 해싱 → 저장 → 이메일 발송
- 완전한 "회원가입" 흐름

✅ **타입 안전성**
- dict 대신 Command/Result DTO 사용
- Value Object로 유효하지 않은 데이터 원천 차단

---

## 6. 실전 체크리스트

### ✅ Use Case 구현 전 자가 진단

내가 지금 만들려는 게 정말 Use Case인가?

- [ ] 이 로직이 **"사용자가 ~한다"**로 표현되는가?
- [ ] **2개 이상의 Service/Repository**를 조합하는가?
- [ ] **트랜잭션 경계**가 필요한가?
- [ ] Facade/Controller가 **비즈니스 로직을 포함**하고 있는가?
- [ ] 이 로직을 **프레임워크 없이 테스트**하고 싶은가?
- [ ] HTTP Request/Response 없이도 **의미가 있는 동작**인가?

**6개 중 4개 이상** → Use Case를 만들어라!

### ✅ Use Case 구현 후 검증

내가 만든 Use Case가 제대로 된 건가?

#### 구조 검증
- [ ] HTTP Request/Response 객체를 **직접 다루지 않는가**?
- [ ] Infrastructure(Redis, 외부 API)를 **직접 호출하지 않는가**?
- [ ] Repository/Adapter **인터페이스로만** Infrastructure 접근하는가?
- [ ] 입력은 **Command/DTO**, 출력도 **DTO/Domain Object**인가?

#### 책임 검증
- [ ] **단순 CRUD 래퍼**가 아닌가? (Repository 메서드 그대로 호출만?)
- [ ] **비즈니스 시나리오**를 구현하는가?
- [ ] **도메인 로직**은 Entity/VO/Domain Service에 위임했는가?
- [ ] **여러 컴포넌트를 조율**하는가?

#### 독립성 검증
- [ ] FastAPI를 다른 프레임워크로 바꿔도 **Use Case는 변경 없는가**?
- [ ] Redis를 Memcached로 바꿔도 **Use Case는 변경 없는가**?
- [ ] PostgreSQL을 MySQL로 바꿔도 **Use Case는 변경 없는가**?

#### 테스트 검증
- [ ] **Mock 객체**로 쉽게 테스트할 수 있는가?
- [ ] **FastAPI 없이** 단위 테스트가 가능한가?
- [ ] 테스트 코드가 **비즈니스 요구사항**을 표현하는가?

---

### 📊 리팩토링 우선순위

다음 순서로 리팩토링하라:

#### 1단계: Infrastructure 추상화 (우선순위: 🔥 High)
```python
# ❌ Before
class UserUseCase:
    async def set_user_in_redis(self, user, redis=Provide["redis"]):
        await redis.set(...)  # Redis 직접 의존

# ✅ After
class LoginUseCase:
    def __init__(self, cache_repo: CacheRepository):  # 인터페이스 의존
        self.cache_repo = cache_repo

    async def execute(self, command):
        await self.cache_repo.set_user_session(user, tokens)
```

**이유:** Infrastructure 의존은 테스트와 유연성을 심각하게 해침

#### 2단계: Use Case에 비즈니스 시나리오 이동 (우선순위: 🔥 High)
```python
# ❌ Before - Facade가 시나리오 처리
class AuthFacade:
    async def login(self, request, username, password):
        user = await self.auth_service.authenticate(...)
        user_with_token = await self.token_service.get_token(...)
        await self.user_service.save_user_in_redis(...)

# ✅ After - Use Case가 시나리오 처리
class LoginUseCase:
    async def execute(self, command: LoginCommand) -> LoginResult:
        user = await self.auth_service.authenticate(...)
        tokens = self.token_service.create_tokens(...)
        await self.cache_repo.set_user_session(...)
        return LoginResult(...)
```

**이유:** 비즈니스 로직이 프레임워크에 종속되면 재사용/테스트 불가

#### 3단계: Command/Result DTO 도입 (우선순위: 🟡 Medium)
```python
# ❌ Before
async def login(request: Request, username: str, password: str):
    ...

# ✅ After
async def execute(self, command: LoginCommand) -> LoginResult:
    ...
```

**이유:** 타입 안전성, 프레임워크 독립성, 명확한 계약

#### 4단계: Value Object 도입 (우선순위: 🟡 Medium)
```python
# ❌ Before
def validate_email(email: str) -> bool:
    ...

# ✅ After
@dataclass(frozen=True)
class Email:
    value: str
    def __post_init__(self):
        if not self._is_valid(self.value):
            raise InvalidEmailEx()
```

**이유:** 도메인 규칙을 타입 시스템으로 강제, 유효하지 않은 상태 원천 차단

#### 5단계: Domain Event 도입 (우선순위: 🟢 Low, 선택)
```python
# 이메일 발송을 동기가 아닌 이벤트로 처리
class RegisterUserUseCase:
    async def execute(self, command):
        user = await self.user_repo.save(...)

        # 이벤트 발행
        await self.event_bus.publish(
            UserRegisteredEvent(user_id=user.user_id, email=user.email)
        )

        return result
```

**이유:** 트랜잭션 경계 분리, 확장성, 하지만 복잡도 증가

---

## 7. 마무리: "Use Case를 안 쓸 수 없게 되는" 이유

### 🎯 Use Case가 해결하는 문제

#### 문제 1: "비즈니스 로직이 어디에 있지?"

**Before (Use Case 없이):**
```
Controller에? Service에? Facade에? Repository에?
→ 팀원마다 다른 곳에 넣음
→ 코드 리뷰 때마다 논쟁
→ 유지보수 악몽
```

**After (Use Case 사용):**
```
비즈니스 시나리오 = Use Case
도메인 규칙 = Entity/VO/Domain Service
Infrastructure = Repository/Adapter
→ 명확한 경계, 논쟁 종료
```

#### 문제 2: "프레임워크를 바꾸면 전체 재작성?"

**Before:**
```python
# FastAPI에 종속
@router.post("/login")
async def login(request: Request, response: Response):
    user = await auth_service.authenticate(request.form_data)
    response.set_cookie("token", ...)
    return JSONResponse(...)
```

→ Spring으로 변경? 전체 재작성

**After:**
```python
# Use Case는 프레임워크 독립
class LoginUseCase:
    async def execute(self, command: LoginCommand) -> LoginResult:
        ...

# FastAPI 어댑터
@router.post("/login")
async def login(form: Form, usecase: LoginUseCase):
    command = LoginCommand(...)
    result = await usecase.execute(command)
    return to_response(result)

# Spring 어댑터 (Use Case 재사용!)
@PostMapping("/login")
public ResponseEntity login(@RequestBody LoginRequest req) {
    LoginCommand command = ...
    LoginResult result = loginUseCase.execute(command);
    return toResponse(result);
}
```

#### 문제 3: "테스트를 어떻게 짜지?"

**Before (Facade/Controller에 로직):**
```python
# 테스트하려면 FastAPI 전체 띄워야 함
async def test_login():
    client = TestClient(app)  # 무거움
    response = client.post("/login", data={...})
    assert response.status_code == 200
```

→ 느리고, 깨지기 쉽고, 통합 테스트만 가능

**After (Use Case 사용):**
```python
# 순수 Python 객체로 빠른 단위 테스트
async def test_login_success():
    # Mock으로 의존성 주입
    mock_auth = Mock(spec=AuthenticationService)
    mock_token = Mock(spec=TokenService)
    mock_cache = Mock(spec=CacheRepository)

    usecase = LoginUseCase(mock_auth, mock_token, mock_cache, config)

    command = LoginCommand(login_id="test", password="test123")
    result = await usecase.execute(command)

    assert result.login_id == "test"
    assert result.access_token is not None
    mock_cache.set_user_session.assert_called_once()

# 프레임워크 없이 초고속 테스트 가능!
```

---

### 🚀 실천 가이드

#### Step 1: 가장 복잡한 Use Case 1개부터 시작

```python
# "로그인" Use Case부터 리팩토링
# 1. LoginCommand/LoginResult DTO 정의
# 2. CacheRepository 인터페이스 정의
# 3. LoginUseCase 구현
# 4. Endpoint를 얇게 변경
# 5. 단위 테스트 작성
```

#### Step 2: 팀에 공유하고 피드백

```markdown
## 리팩토링 Before/After 비교

### Before
- 비즈니스 로직이 Facade에 분산
- Redis 직접 의존
- 테스트 어려움

### After
- Use Case에 시나리오 집중
- Infrastructure 추상화
- 단위 테스트 가능

### 성과
- 테스트 속도 10배 향상 (3초 → 0.3초)
- 코드 재사용성 증가
- 프레임워크 독립성 확보
```

#### Step 3: 점진적 확장

```
1주차: Login Use Case
2주차: Register Use Case
3주차: RefreshToken Use Case
4주차: 팀 컨벤션 문서화
5주차: 새로운 기능은 Use Case 패턴으로
```

---

### 📚 참고 자료

- **Clean Architecture (Robert C. Martin)** - Use Case 개념의 원조
- **Domain-Driven Design (Eric Evans)** - Application Service vs Domain Service
- **Implementing Domain-Driven Design (Vaughn Vernon)** - 실전 Use Case 구현
- **Get Your Hands Dirty on Clean Architecture (Tom Hombergs)** - Hexagonal Architecture + Use Case

---

### 💡 핵심 요약

```
Use Case = "사용자가 시스템으로 달성하려는 완전한 비즈니스 목표의 구현체"

Use Case가 하는 것:
✅ 비즈니스 시나리오 오케스트레이션
✅ 도메인 객체 조율
✅ 트랜잭션 경계 정의

Use Case가 하지 않는 것:
❌ HTTP 요청/응답 처리 → Controller
❌ 도메인 규칙 검증 → Entity/VO
❌ 데이터 접근 → Repository
❌ Infrastructure 직접 호출 → Adapter

판단 기준:
"이 로직을 FastAPI 없이 테스트할 수 있는가?"
"이 로직이 '사용자가 ~한다'로 표현되는가?"
"2개 이상의 컴포넌트를 조합하는가?"

→ YES면 Use Case로!
```

---

이 문서를 읽고 나면, **Use Case 없이 코드를 짜는 게 불편해질 것입니다.**

그게 바로 목표였습니다. 🎯
