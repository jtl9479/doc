# 15장: 파일 업로드 (Part 2 - 실무편)

> **학습 목표**: 실무에서 필요한 파일 업로드 고급 기능(클라우드 스토리지, 이미지 처리, Ajax 업로드)을 구현할 수 있습니다.

**⏱️ 예상 학습 시간**: 4-5시간
**난이도**: ⭐⭐⭐⭐☆ (4개/5개)

---

## 📚 목차
- [실무 활용 사례](#실무-활용-사례)
- [주니어 시나리오](#주니어-시나리오)
- [실전 프로젝트](#실전-프로젝트)
- [고급 기능](#고급-기능)
- [핵심 정리](#핵심-정리)

---

## 🏢 실무 활용 사례

### 사례 1: 카카오톡 - 프로필 사진 업로드

**배경**: 수백만 사용자가 프로필 사진을 업로드하고, 다양한 크기로 표시

**요구사항**:
- 원본 이미지 저장
- 썸네일 자동 생성 (50x50, 150x150, 300x300)
- S3에 저장 (확장성)
- CDN 연동 (빠른 로딩)

**구현**:

#### 의존성 추가

```xml
<!-- AWS S3 -->
<dependency>
    <groupId>com.amazonaws</groupId>
    <artifactId>aws-java-sdk-s3</artifactId>
    <version>1.12.565</version>
</dependency>

<!-- 이미지 처리 (Thumbnailator) -->
<dependency>
    <groupId>net.coobird</groupId>
    <artifactId>thumbnailator</artifactId>
    <version>0.4.19</version>
</dependency>
```

#### S3 설정

```yaml
# application.yml
cloud:
  aws:
    credentials:
      access-key: ${AWS_ACCESS_KEY}
      secret-key: ${AWS_SECRET_KEY}
    s3:
      bucket: kakaotalk-profiles
      region: ap-northeast-2
    cloudfront:
      domain: https://d1234567890.cloudfront.net
```

#### S3 Service

```java
package com.kakaotalk.service;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.CannedAccessControlList;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;
import lombok.RequiredArgsConstructor;
import net.coobird.thumbnailator.Thumbnails;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class S3ProfileImageService {

    private final AmazonS3 amazonS3;

    @Value("${cloud.aws.s3.bucket}")
    private String bucket;

    @Value("${cloud.aws.cloudfront.domain}")
    private String cloudFrontDomain;

    // 썸네일 크기 정의
    private static final int[] THUMBNAIL_SIZES = {50, 150, 300};

    public ProfileImageUploadResult uploadProfileImage(
        Long userId,
        MultipartFile file
    ) throws IOException {

        // 1. 이미지 검증
        validateImage(file);

        // 2. 원본 이미지 읽기
        BufferedImage originalImage = ImageIO.read(file.getInputStream());

        // 3. 고유 파일명 생성
        String baseFilename = String.format("profiles/%d/%s",
            userId,
            UUID.randomUUID().toString()
        );

        Map<String, String> uploadedUrls = new HashMap<>();

        // 4. 원본 이미지 업로드
        String originalKey = baseFilename + "_original.jpg";
        uploadToS3(originalKey, file.getInputStream(), file.getSize(), file.getContentType());
        uploadedUrls.put("original", getCloudFrontUrl(originalKey));

        // 5. 썸네일 생성 및 업로드
        for (int size : THUMBNAIL_SIZES) {
            ByteArrayOutputStream thumbnailStream = new ByteArrayOutputStream();

            // Thumbnailator로 리사이징
            Thumbnails.of(originalImage)
                .size(size, size)
                .outputFormat("jpg")
                .outputQuality(0.85)
                .toOutputStream(thumbnailStream);

            byte[] thumbnailBytes = thumbnailStream.toByteArray();

            // S3 업로드
            String thumbnailKey = String.format("%s_%dx%d.jpg", baseFilename, size, size);
            uploadToS3(
                thumbnailKey,
                new ByteArrayInputStream(thumbnailBytes),
                thumbnailBytes.length,
                "image/jpeg"
            );

            uploadedUrls.put("thumbnail_" + size, getCloudFrontUrl(thumbnailKey));
        }

        // 6. 결과 반환
        return ProfileImageUploadResult.builder()
            .userId(userId)
            .originalUrl(uploadedUrls.get("original"))
            .thumbnail50Url(uploadedUrls.get("thumbnail_50"))
            .thumbnail150Url(uploadedUrls.get("thumbnail_150"))
            .thumbnail300Url(uploadedUrls.get("thumbnail_300"))
            .build();
    }

    private void uploadToS3(String key, InputStream inputStream, long contentLength, String contentType) {
        ObjectMetadata metadata = new ObjectMetadata();
        metadata.setContentLength(contentLength);
        metadata.setContentType(contentType);

        PutObjectRequest request = new PutObjectRequest(bucket, key, inputStream, metadata)
            .withCannedAcl(CannedAccessControlList.PublicRead);  // 공개 읽기

        amazonS3.putObject(request);
    }

    private String getCloudFrontUrl(String key) {
        return cloudFrontDomain + "/" + key;
    }

    private void validateImage(MultipartFile file) {
        // 크기 검증 (5MB)
        if (file.getSize() > 5 * 1024 * 1024) {
            throw new IllegalArgumentException("이미지 크기는 5MB 이하여야 합니다");
        }

        // MIME 타입 검증
        String contentType = file.getContentType();
        if (!contentType.startsWith("image/")) {
            throw new IllegalArgumentException("이미지 파일만 업로드 가능합니다");
        }

        // 확장자 검증
        String filename = file.getOriginalFilename();
        String extension = filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();
        if (!Arrays.asList("jpg", "jpeg", "png").contains(extension)) {
            throw new IllegalArgumentException("JPG, PNG 파일만 업로드 가능합니다");
        }
    }
}
```

#### Controller

```java
@RestController
@RequestMapping("/api/profile")
@RequiredArgsConstructor
public class ProfileController {

    private final S3ProfileImageService s3ProfileImageService;
    private final UserService userService;

    @PostMapping("/image")
    public ResponseEntity<ProfileImageResponse> uploadProfileImage(
        @AuthenticationPrincipal CustomUserDetails userDetails,
        @RequestParam("image") MultipartFile image
    ) {
        try {
            // 프로필 이미지 업로드
            ProfileImageUploadResult result = s3ProfileImageService.uploadProfileImage(
                userDetails.getUserId(),
                image
            );

            // DB 업데이트
            userService.updateProfileImage(
                userDetails.getUserId(),
                result.getOriginalUrl(),
                result.getThumbnail150Url()
            );

            // 응답
            ProfileImageResponse response = ProfileImageResponse.builder()
                .thumbnailUrl(result.getThumbnail150Url())
                .originalUrl(result.getOriginalUrl())
                .message("프로필 사진이 변경되었습니다")
                .build();

            return ResponseEntity.ok(response);

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                .body(ProfileImageResponse.error(e.getMessage()));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ProfileImageResponse.error("이미지 업로드 실패"));
        }
    }
}
```

#### 프론트엔드 (JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
    <title>프로필 사진 변경</title>
    <style>
        #preview {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #ccc;
        }
        #upload-progress {
            display: none;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>프로필 사진 변경</h1>

    <!-- 현재 프로필 사진 -->
    <img id="preview" src="/images/default-profile.jpg" alt="프로필 사진">

    <!-- 파일 선택 -->
    <input type="file" id="fileInput" accept="image/*">

    <!-- 업로드 버튼 -->
    <button onclick="uploadProfileImage()">변경</button>

    <!-- 프로그레스 바 -->
    <div id="upload-progress">
        <progress id="progressBar" value="0" max="100"></progress>
        <span id="progressText">0%</span>
    </div>

    <script>
        // 파일 선택 시 미리보기
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('preview').src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });

        // 프로필 이미지 업로드
        function uploadProfileImage() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];

            if (!file) {
                alert('파일을 선택해주세요');
                return;
            }

            // FormData 생성
            const formData = new FormData();
            formData.append('image', file);

            // XMLHttpRequest로 업로드 (프로그레스 바 지원)
            const xhr = new XMLHttpRequest();

            // 업로드 진행률
            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    document.getElementById('progressBar').value = percent;
                    document.getElementById('progressText').textContent = Math.round(percent) + '%';
                    document.getElementById('upload-progress').style.display = 'block';
                }
            });

            // 업로드 완료
            xhr.addEventListener('load', function() {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    document.getElementById('preview').src = response.thumbnailUrl;
                    alert('프로필 사진이 변경되었습니다');
                } else {
                    const error = JSON.parse(xhr.responseText);
                    alert('업로드 실패: ' + error.message);
                }
                document.getElementById('upload-progress').style.display = 'none';
            });

            // 에러 처리
            xhr.addEventListener('error', function() {
                alert('업로드 중 오류가 발생했습니다');
                document.getElementById('upload-progress').style.display = 'none';
            });

            // 요청 전송
            xhr.open('POST', '/api/profile/image');
            xhr.setRequestHeader('Authorization', 'Bearer ' + getAccessToken());
            xhr.send(formData);
        }

        function getAccessToken() {
            // JWT 토큰 반환
            return localStorage.getItem('accessToken');
        }
    </script>
</body>
</html>
```

**성과**:
- **S3 저장**: 서버 디스크 용량 걱정 없음
- **썸네일 자동 생성**: 수동 작업 **100% 자동화**
- **CDN 연동**: 이미지 로딩 속도 **70% 향상**
- **확장성**: 사용자 증가에도 안정적

---

### 사례 2: 배달의민족 - 음식점 메뉴 사진 업로드

**배경**: 음식점 사장님들이 메뉴 사진을 여러 장 업로드

**요구사항**:
- 한 번에 최대 10장 업로드
- 이미지 리사이징 (모바일 최적화)
- 워터마크 추가 (저작권 보호)
- 드래그 앤 드롭 지원

**구현**:

#### 여러 파일 업로드 Service

```java
@Service
@RequiredArgsConstructor
public class MenuImageService {

    private final FileStorageService fileStorageService;
    private final ImageProcessor imageProcessor;

    public List<MenuImageResult> uploadMenuImages(
        Long restaurantId,
        List<MultipartFile> images
    ) throws IOException {

        // 1. 이미지 개수 검증 (최대 10개)
        if (images.size() > 10) {
            throw new IllegalArgumentException("한 번에 최대 10장까지 업로드 가능합니다");
        }

        List<MenuImageResult> results = new ArrayList<>();

        for (MultipartFile image : images) {
            // 2. 각 이미지 처리
            MenuImageResult result = processMenuImage(restaurantId, image);
            results.add(result);
        }

        return results;
    }

    private MenuImageResult processMenuImage(Long restaurantId, MultipartFile image) throws IOException {
        // 1. 이미지 읽기
        BufferedImage originalImage = ImageIO.read(image.getInputStream());

        // 2. 리사이징 (1200px 너비, 비율 유지)
        BufferedImage resizedImage = imageProcessor.resize(originalImage, 1200, -1);

        // 3. 워터마크 추가
        BufferedImage watermarkedImage = imageProcessor.addWatermark(
            resizedImage,
            "배달의민족",
            0.3f  // 투명도 30%
        );

        // 4. 압축 (JPEG 품질 85%)
        byte[] compressedImage = imageProcessor.compress(watermarkedImage, 0.85f);

        // 5. S3 업로드
        String filename = String.format("menus/%d/%s.jpg",
            restaurantId,
            UUID.randomUUID().toString()
        );

        String imageUrl = fileStorageService.uploadToS3(
            filename,
            new ByteArrayInputStream(compressedImage),
            "image/jpeg"
        );

        return MenuImageResult.builder()
            .imageUrl(imageUrl)
            .originalFilename(image.getOriginalFilename())
            .size(compressedImage.length)
            .build();
    }
}
```

#### 이미지 프로세서

```java
@Component
public class ImageProcessor {

    /**
     * 이미지 리사이징
     * @param width 목표 너비 (-1이면 비율 유지)
     * @param height 목표 높이 (-1이면 비율 유지)
     */
    public BufferedImage resize(BufferedImage original, int width, int height) throws IOException {
        if (width == -1 && height == -1) {
            return original;
        }

        // 비율 계산
        int originalWidth = original.getWidth();
        int originalHeight = original.getHeight();

        if (width == -1) {
            width = (int) (originalWidth * ((double) height / originalHeight));
        } else if (height == -1) {
            height = (int) (originalHeight * ((double) width / originalWidth));
        }

        return Thumbnails.of(original)
            .size(width, height)
            .asBufferedImage();
    }

    /**
     * 워터마크 추가
     */
    public BufferedImage addWatermark(BufferedImage image, String text, float alpha) {
        int width = image.getWidth();
        int height = image.getHeight();

        // 새 이미지 생성
        BufferedImage watermarked = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = watermarked.createGraphics();

        // 원본 이미지 그리기
        g.drawImage(image, 0, 0, null);

        // 워터마크 설정
        g.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, alpha));
        g.setColor(Color.WHITE);
        g.setFont(new Font("Arial", Font.BOLD, 48));

        // 텍스트 크기 측정
        FontMetrics fm = g.getFontMetrics();
        int textWidth = fm.stringWidth(text);
        int textHeight = fm.getHeight();

        // 우측 하단에 워터마크 그리기
        int x = width - textWidth - 20;
        int y = height - 20;
        g.drawString(text, x, y);

        g.dispose();

        return watermarked;
    }

    /**
     * JPEG 압축
     */
    public byte[] compress(BufferedImage image, float quality) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();

        // JPEG Writer 가져오기
        Iterator<ImageWriter> writers = ImageIO.getImageWritersByFormatName("jpg");
        ImageWriter writer = writers.next();

        // 압축 품질 설정
        ImageWriteParam param = writer.getDefaultWriteParam();
        param.setCompressionMode(ImageWriteParam.MODE_EXPLICIT);
        param.setCompressionQuality(quality);

        // 이미지 쓰기
        writer.setOutput(new MemoryCacheImageOutputStream(baos));
        writer.write(null, new IIOImage(image, null, null), param);
        writer.dispose();

        return baos.toByteArray();
    }
}
```

#### Drag & Drop 프론트엔드

```html
<!DOCTYPE html>
<html>
<head>
    <title>메뉴 사진 업로드</title>
    <style>
        #drop-zone {
            border: 3px dashed #ccc;
            border-radius: 10px;
            width: 100%;
            height: 200px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 18px;
            color: #999;
            transition: all 0.3s;
        }

        #drop-zone.dragover {
            border-color: #007bff;
            background-color: #f0f8ff;
            color: #007bff;
        }

        .preview-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 20px;
        }

        .preview-item {
            position: relative;
            width: 150px;
            height: 150px;
        }

        .preview-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 5px;
        }

        .preview-item .remove-btn {
            position: absolute;
            top: 5px;
            right: 5px;
            background-color: red;
            color: white;
            border: none;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            cursor: pointer;
        }

        .upload-status {
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>메뉴 사진 업로드</h1>

    <!-- Drag & Drop 영역 -->
    <div id="drop-zone">
        이미지를 드래그하여 놓거나 클릭하여 선택하세요
    </div>

    <input type="file" id="fileInput" multiple accept="image/*" style="display: none;">

    <!-- 미리보기 -->
    <div class="preview-container" id="preview-container"></div>

    <!-- 업로드 버튼 -->
    <button onclick="uploadImages()" style="margin-top: 20px;">업로드</button>

    <!-- 상태 -->
    <div class="upload-status" id="upload-status"></div>

    <script>
        let selectedFiles = [];

        // Drag & Drop 이벤트
        const dropZone = document.getElementById('drop-zone');

        dropZone.addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');

            const files = Array.from(e.dataTransfer.files);
            addFiles(files);
        });

        // 파일 선택 이벤트
        document.getElementById('fileInput').addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            addFiles(files);
        });

        // 파일 추가
        function addFiles(files) {
            // 이미지 파일만 필터링
            const imageFiles = files.filter(file => file.type.startsWith('image/'));

            // 최대 10개 제한
            if (selectedFiles.length + imageFiles.length > 10) {
                alert('최대 10장까지 업로드 가능합니다');
                return;
            }

            selectedFiles = selectedFiles.concat(imageFiles);
            displayPreviews();
        }

        // 미리보기 표시
        function displayPreviews() {
            const container = document.getElementById('preview-container');
            container.innerHTML = '';

            selectedFiles.forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const div = document.createElement('div');
                    div.className = 'preview-item';

                    const img = document.createElement('img');
                    img.src = e.target.result;

                    const removeBtn = document.createElement('button');
                    removeBtn.className = 'remove-btn';
                    removeBtn.textContent = '×';
                    removeBtn.onclick = () => removeFile(index);

                    div.appendChild(img);
                    div.appendChild(removeBtn);
                    container.appendChild(div);
                };
                reader.readAsDataURL(file);
            });
        }

        // 파일 제거
        function removeFile(index) {
            selectedFiles.splice(index, 1);
            displayPreviews();
        }

        // 업로드
        async function uploadImages() {
            if (selectedFiles.length === 0) {
                alert('업로드할 이미지를 선택해주세요');
                return;
            }

            const formData = new FormData();
            selectedFiles.forEach(file => {
                formData.append('images', file);
            });

            const statusDiv = document.getElementById('upload-status');
            statusDiv.textContent = '업로드 중...';

            try {
                const response = await fetch('/api/menu/images', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + getAccessToken()
                    },
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    statusDiv.textContent = `업로드 완료: ${result.uploadedCount}개`;
                    selectedFiles = [];
                    displayPreviews();
                } else {
                    const error = await response.json();
                    statusDiv.textContent = '업로드 실패: ' + error.message;
                }
            } catch (error) {
                statusDiv.textContent = '업로드 중 오류 발생';
                console.error(error);
            }
        }

        function getAccessToken() {
            return localStorage.getItem('accessToken');
        }
    </script>
</body>
</html>
```

**성과**:
- **드래그 앤 드롭**: 사용자 편의성 **80% 향상**
- **자동 리사이징**: 모바일 로딩 속도 **60% 개선**
- **워터마크**: 저작권 침해 **90% 감소**
- **일괄 업로드**: 사장님 작업 시간 **75% 단축**

---

### 사례 3: 구글 드라이브 - 대용량 파일 청크 업로드

**배경**: 1GB 이상 대용량 파일도 안정적으로 업로드

**요구사항**:
- 파일을 작은 청크로 분할 (5MB 단위)
- 네트워크 오류 시 재시도
- 업로드 일시정지/재개
- 프로그레스 바 표시

**구현**:

#### 청크 업로드 Controller

```java
@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class ChunkUploadController {

    private final ChunkUploadService chunkUploadService;

    /**
     * 청크 업로드 초기화
     */
    @PostMapping("/upload/init")
    public ResponseEntity<ChunkUploadInitResponse> initChunkUpload(
        @RequestBody ChunkUploadInitRequest request
    ) {
        String uploadId = chunkUploadService.initUpload(
            request.getFilename(),
            request.getTotalSize(),
            request.getTotalChunks()
        );

        return ResponseEntity.ok(
            new ChunkUploadInitResponse(uploadId)
        );
    }

    /**
     * 청크 업로드
     */
    @PostMapping("/upload/chunk")
    public ResponseEntity<ChunkUploadResponse> uploadChunk(
        @RequestParam("uploadId") String uploadId,
        @RequestParam("chunkIndex") int chunkIndex,
        @RequestParam("chunk") MultipartFile chunk
    ) throws IOException {

        chunkUploadService.uploadChunk(uploadId, chunkIndex, chunk);

        return ResponseEntity.ok(
            new ChunkUploadResponse(uploadId, chunkIndex, "success")
        );
    }

    /**
     * 청크 업로드 완료
     */
    @PostMapping("/upload/complete")
    public ResponseEntity<FileUploadResult> completeChunkUpload(
        @RequestParam("uploadId") String uploadId
    ) throws IOException {

        FileUploadResult result = chunkUploadService.completeUpload(uploadId);

        return ResponseEntity.ok(result);
    }
}
```

#### 청크 업로드 Service

```java
@Service
public class ChunkUploadService {

    private final Map<String, ChunkUploadSession> uploadSessions = new ConcurrentHashMap<>();

    @Value("${file.upload-dir}")
    private String uploadDir;

    /**
     * 업로드 초기화
     */
    public String initUpload(String filename, long totalSize, int totalChunks) {
        String uploadId = UUID.randomUUID().toString();

        ChunkUploadSession session = ChunkUploadSession.builder()
            .uploadId(uploadId)
            .filename(filename)
            .totalSize(totalSize)
            .totalChunks(totalChunks)
            .uploadedChunks(new HashSet<>())
            .createdAt(LocalDateTime.now())
            .build();

        uploadSessions.put(uploadId, session);

        // 임시 디렉토리 생성
        Path tempDir = Paths.get(uploadDir, "temp", uploadId);
        try {
            Files.createDirectories(tempDir);
        } catch (IOException e) {
            throw new RuntimeException("임시 디렉토리 생성 실패", e);
        }

        return uploadId;
    }

    /**
     * 청크 업로드
     */
    public void uploadChunk(String uploadId, int chunkIndex, MultipartFile chunk) throws IOException {
        ChunkUploadSession session = uploadSessions.get(uploadId);
        if (session == null) {
            throw new IllegalArgumentException("유효하지 않은 uploadId입니다");
        }

        // 청크 저장
        Path tempDir = Paths.get(uploadDir, "temp", uploadId);
        Path chunkPath = tempDir.resolve(String.format("chunk_%d", chunkIndex));

        chunk.transferTo(chunkPath);

        // 업로드된 청크 기록
        session.getUploadedChunks().add(chunkIndex);
    }

    /**
     * 업로드 완료 (청크 병합)
     */
    public FileUploadResult completeUpload(String uploadId) throws IOException {
        ChunkUploadSession session = uploadSessions.get(uploadId);
        if (session == null) {
            throw new IllegalArgumentException("유효하지 않은 uploadId입니다");
        }

        // 모든 청크가 업로드되었는지 확인
        if (session.getUploadedChunks().size() != session.getTotalChunks()) {
            throw new IllegalStateException("아직 업로드되지 않은 청크가 있습니다");
        }

        // 청크 병합
        Path tempDir = Paths.get(uploadDir, "temp", uploadId);
        Path finalFile = Paths.get(uploadDir, session.getFilename());

        try (FileOutputStream fos = new FileOutputStream(finalFile.toFile())) {
            for (int i = 0; i < session.getTotalChunks(); i++) {
                Path chunkPath = tempDir.resolve(String.format("chunk_%d", i));
                Files.copy(chunkPath, fos);
            }
        }

        // 임시 파일 삭제
        Files.walk(tempDir)
            .sorted(Comparator.reverseOrder())
            .forEach(path -> {
                try {
                    Files.delete(path);
                } catch (IOException e) {
                    // ignore
                }
            });

        // 세션 제거
        uploadSessions.remove(uploadId);

        return FileUploadResult.builder()
            .filename(session.getFilename())
            .size(session.getTotalSize())
            .uploadedAt(LocalDateTime.now())
            .build();
    }
}
```

#### 프론트엔드 (청크 업로드)

```html
<script>
async function uploadLargeFile(file) {
    const CHUNK_SIZE = 5 * 1024 * 1024;  // 5MB
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

    // 1. 업로드 초기화
    const initResponse = await fetch('/api/files/upload/init', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filename: file.name,
            totalSize: file.size,
            totalChunks: totalChunks
        })
    });

    const { uploadId } = await initResponse.json();

    // 2. 청크 업로드
    for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const chunk = file.slice(start, end);

        const formData = new FormData();
        formData.append('uploadId', uploadId);
        formData.append('chunkIndex', i);
        formData.append('chunk', chunk);

        // 재시도 로직
        let retries = 3;
        while (retries > 0) {
            try {
                await fetch('/api/files/upload/chunk', {
                    method: 'POST',
                    body: formData
                });

                // 프로그레스 업데이트
                const progress = ((i + 1) / totalChunks) * 100;
                updateProgress(progress);

                break;  // 성공
            } catch (error) {
                retries--;
                if (retries === 0) {
                    throw new Error(`청크 ${i} 업로드 실패`);
                }
                await sleep(1000);  // 1초 대기 후 재시도
            }
        }
    }

    // 3. 업로드 완료
    const completeResponse = await fetch('/api/files/upload/complete?uploadId=' + uploadId, {
        method: 'POST'
    });

    const result = await completeResponse.json();
    alert('업로드 완료: ' + result.filename);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function updateProgress(percent) {
    document.getElementById('progressBar').value = percent;
    document.getElementById('progressText').textContent = Math.round(percent) + '%';
}
</script>
```

**성과**:
- **안정성**: 네트워크 오류 시 자동 재시도로 실패율 **95% 감소**
- **재개 가능**: 업로드 중단 후 재개 가능
- **대용량 파일**: 10GB 파일도 안정적 업로드
- **사용자 경험**: 프로그레스 바로 진행 상황 파악

---

## 👨‍💻 주니어 시나리오

### 시나리오 1: "파일이 저장은 되는데 DB에는 저장이 안 돼요!"

**상황**:
주니어 개발자 김코딩이 파일 업로드 기능을 구현했는데, 파일은 서버에 저장되지만 DB에는 파일 정보가 저장되지 않습니다.

```java
// ❌ 주니어 개발자가 작성한 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    // 파일 저장
    String filename = UUID.randomUUID().toString() + "_" + file.getOriginalFilename();
    Path path = Paths.get("uploads/" + filename);
    file.transferTo(path);

    // DB 저장
    UploadedFile uploadedFile = new UploadedFile();
    uploadedFile.setFilename(filename);
    uploadedFile.setFilePath(path.toString());
    uploadedFileRepository.save(uploadedFile);  // 이 부분이 실행 안 됨!

    return "redirect:/success";
}
```

**문제점**:
1. **트랜잭션 처리 없음**: 파일 저장 후 에러 발생 시 롤백 불가
2. **예외 처리 없음**: transferTo()에서 IOException 발생 시 DB 저장 코드 실행 안 됨
3. **검증 없음**: 파일이 실제로 저장되었는지 확인 안 함

**해결책**:

```java
// ✅ 올바른 코드
@PostMapping("/upload")
@Transactional  // ✅ 트랜잭션 추가
public String upload(@RequestParam("file") MultipartFile file,
                    RedirectAttributes redirectAttributes) {

    try {
        // 1. 파일 저장
        String filename = UUID.randomUUID().toString() + "_" + file.getOriginalFilename();
        Path path = Paths.get("uploads/" + filename);

        // ✅ 디렉토리 존재 확인
        if (!Files.exists(path.getParent())) {
            Files.createDirectories(path.getParent());
        }

        file.transferTo(path);

        // ✅ 파일이 실제로 저장되었는지 확인
        if (!Files.exists(path)) {
            throw new IOException("파일 저장 실패: " + filename);
        }

        // 2. DB 저장
        UploadedFile uploadedFile = new UploadedFile();
        uploadedFile.setFilename(file.getOriginalFilename());
        uploadedFile.setStoredFilename(filename);
        uploadedFile.setFilePath(path.toString());
        uploadedFile.setFileSize(file.getSize());
        uploadedFile.setContentType(file.getContentType());
        uploadedFile.setUploadedAt(LocalDateTime.now());

        uploadedFileRepository.save(uploadedFile);

        redirectAttributes.addFlashAttribute("message", "업로드 성공");

    } catch (IOException e) {
        // ✅ 파일 저장 실패 시 처리
        redirectAttributes.addFlashAttribute("message", "파일 저장 실패: " + e.getMessage());
        return "redirect:/upload";
    } catch (Exception e) {
        // ✅ DB 저장 실패 시 처리
        // 트랜잭션 롤백되므로 파일 수동 삭제
        try {
            Files.deleteIfExists(Paths.get("uploads/" + filename));
        } catch (IOException ignored) {
        }

        redirectAttributes.addFlashAttribute("message", "DB 저장 실패: " + e.getMessage());
        return "redirect:/upload";
    }

    return "redirect:/success";
}
```

**더 나은 방법 (Service 분리)**:

```java
@Service
@Transactional
public class FileUploadService {

    @Autowired
    private UploadedFileRepository uploadedFileRepository;

    @Value("${file.upload-dir}")
    private String uploadDir;

    public UploadedFile upload(MultipartFile file) throws IOException {
        // 1. 파일 저장
        String storedFilename = UUID.randomUUID().toString() + "_" + file.getOriginalFilename();
        Path path = Paths.get(uploadDir, storedFilename);

        if (!Files.exists(path.getParent())) {
            Files.createDirectories(path.getParent());
        }

        file.transferTo(path);

        if (!Files.exists(path)) {
            throw new IOException("파일 저장 실패");
        }

        // 2. DB 저장
        UploadedFile uploadedFile = UploadedFile.builder()
            .originalFilename(file.getOriginalFilename())
            .storedFilename(storedFilename)
            .filePath(path.toString())
            .fileSize(file.getSize())
            .contentType(file.getContentType())
            .uploadedAt(LocalDateTime.now())
            .build();

        return uploadedFileRepository.save(uploadedFile);
    }

    @Transactional
    public void delete(Long fileId) throws IOException {
        UploadedFile file = uploadedFileRepository.findById(fileId)
            .orElseThrow(() -> new IllegalArgumentException("파일을 찾을 수 없습니다"));

        // 1. 실제 파일 삭제
        Files.deleteIfExists(Paths.get(file.getFilePath()));

        // 2. DB 삭제
        uploadedFileRepository.delete(file);
    }
}
```

**배운 점**:
- 💡 @Transactional 사용으로 원자성 보장
- 💡 예외 처리로 에러 상황 대응
- 💡 Service 레이어 분리로 책임 분리
- 💡 파일 저장 후 존재 여부 확인

---

### 시나리오 2: "이미지를 업로드하면 화면에 안 나와요!"

**상황**:
주니어 개발자 박초보가 이미지를 업로드했는데, 화면에 이미지가 표시되지 않습니다.

```java
// ❌ Controller
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    String filename = UUID.randomUUID().toString() + ".jpg";
    Path path = Paths.get("uploads/" + filename);
    file.transferTo(path);

    return "redirect:/view?filename=" + filename;
}

@GetMapping("/view")
public String view(@RequestParam String filename, Model model) {
    model.addAttribute("imageUrl", "uploads/" + filename);
    return "view";
}
```

```html
<!-- ❌ view.html -->
<img th:src="${imageUrl}" alt="이미지">
<!-- 화면에 안 나옴! -->
```

**문제점**:
1. **정적 리소스 매핑 없음**: Spring이 /uploads/ 경로를 모름
2. **파일 다운로드 Controller 없음**: 이미지 파일에 접근할 방법이 없음

**해결책 1: 정적 리소스 매핑**

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${file.upload-dir}")
    private String uploadDir;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // ✅ /uploads/** 경로를 실제 파일 시스템 경로로 매핑
        registry.addResourceHandler("/uploads/**")
            .addResourceLocations("file:" + uploadDir + "/");
    }
}
```

```html
<!-- ✅ view.html -->
<img th:src="@{/uploads/{filename}(filename=${filename})}" alt="이미지">
<!-- 이제 나옴! -->
```

**해결책 2: 파일 다운로드 Controller (더 안전)**

```java
@GetMapping("/files/{id}")
public ResponseEntity<Resource> downloadFile(@PathVariable Long id) {
    // 1. DB에서 파일 정보 조회
    UploadedFile uploadedFile = uploadedFileRepository.findById(id)
        .orElseThrow(() -> new IllegalArgumentException("파일을 찾을 수 없습니다"));

    // 2. 파일 읽기
    Path path = Paths.get(uploadedFile.getFilePath());
    Resource resource = new FileSystemResource(path);

    if (!resource.exists()) {
        throw new RuntimeException("파일이 존재하지 않습니다");
    }

    // 3. 응답
    return ResponseEntity.ok()
        .contentType(MediaType.parseMediaType(uploadedFile.getContentType()))
        .header(HttpHeaders.CONTENT_DISPOSITION,
            "inline; filename=\"" + uploadedFile.getOriginalFilename() + "\"")
        .body(resource);
}
```

```html
<!-- ✅ view.html -->
<img th:src="@{/files/{id}(id=${fileId})}" alt="이미지">
<!-- DB를 통한 안전한 접근 -->
```

**배운 점**:
- 💡 정적 리소스는 WebMvcConfigurer로 매핑
- 💡 보안을 위해서는 Controller를 통한 접근이 더 안전
- 💡 파일 경로를 직접 노출하지 않음
- 💡 DB를 통한 권한 확인 가능

---

### 시나리오 3: "파일 업로드가 너무 느려요!"

**상황**:
주니어 개발자 이신입이 파일 업로드를 구현했는데, 1MB 파일도 10초 이상 걸립니다.

```java
// ❌ 느린 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) throws IOException {
    // ❌ getBytes()로 전체를 메모리에 로드
    byte[] bytes = file.getBytes();

    // ❌ 바이트 배열을 하나씩 쓰기
    FileOutputStream fos = new FileOutputStream("uploads/" + file.getOriginalFilename());
    for (byte b : bytes) {
        fos.write(b);  // 매우 느림!
    }
    fos.close();

    return "redirect:/success";
}
```

**문제점**:
1. **getBytes() 사용**: 파일 전체를 메모리에 로드
2. **바이트 단위 쓰기**: I/O 작업이 바이트마다 발생
3. **버퍼 미사용**: 디스크 접근이 너무 많음

**해결책**:

```java
// ✅ 빠른 코드
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) throws IOException {
    Path path = Paths.get("uploads/" + file.getOriginalFilename());

    // ✅ transferTo() 사용: 스트리밍 + 버퍼링
    file.transferTo(path);

    return "redirect:/success";
}
```

**성능 비교**:

| 방법 | 1MB 파일 | 100MB 파일 | 메모리 사용 |
|------|----------|------------|-------------|
| 바이트 단위 쓰기 | 10초 | 1000초 | 100MB |
| getBytes() + write() | 2초 | 200초 | 100MB |
| transferTo() | 0.1초 | 10초 | 1MB |

**더 빠르게: 비동기 업로드**

```java
@Service
public class AsyncFileUploadService {

    @Async
    public CompletableFuture<String> uploadAsync(MultipartFile file) throws IOException {
        String filename = UUID.randomUUID().toString() + "_" + file.getOriginalFilename();
        Path path = Paths.get("uploads/" + filename);

        file.transferTo(path);

        return CompletableFuture.completedFuture(filename);
    }
}

@RestController
public class AsyncUploadController {

    @Autowired
    private AsyncFileUploadService asyncFileUploadService;

    @PostMapping("/upload/async")
    public CompletableFuture<ResponseEntity<String>> uploadAsync(
        @RequestParam("file") MultipartFile file
    ) {
        return asyncFileUploadService.uploadAsync(file)
            .thenApply(filename ->
                ResponseEntity.ok("업로드 완료: " + filename)
            )
            .exceptionally(ex ->
                ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("업로드 실패: " + ex.getMessage())
            );
    }
}
```

**배운 점**:
- 💡 transferTo() 사용으로 성능 100배 향상
- 💡 @Async로 비동기 처리 가능
- 💡 버퍼 크기가 성능에 큰 영향
- 💡 메모리 사용량도 중요

---

## 🛠️ 실전 프로젝트

### 프로젝트: 게시판 첨부파일 시스템

**난이도**: ⭐⭐⭐⭐☆
**예상 소요 시간**: 6-8시간
**학습 목표**: 실무에서 사용되는 완전한 파일 업로드 시스템 구축

### 요구사항 분석

#### 기능 요구사항
- [ ] 게시글 작성 시 파일 여러 개 첨부 (최대 5개)
- [ ] 파일 다운로드 (다운로드 횟수 기록)
- [ ] 파일 삭제 (작성자만)
- [ ] 이미지 미리보기
- [ ] 파일 크기 제한 (개당 10MB, 전체 50MB)
- [ ] 허용 확장자: 이미지(jpg, png), 문서(pdf, docx), 압축(zip)

#### 기술 요구사항
- [ ] Spring Boot 3.x
- [ ] JPA + MySQL
- [ ] Thymeleaf
- [ ] 파일 검증 (확장자, 크기, MIME)
- [ ] 에러 처리
- [ ] 트랜잭션 관리

#### 비기능 요구사항
- [ ] 파일 업로드 성공률 99% 이상
- [ ] 100MB 파일 업로드 시간 10초 이내
- [ ] 동시 업로드 100명 지원

### 프로젝트 구조

```
project/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/board/
│   │   │       ├── controller/
│   │   │       │   ├── BoardController.java
│   │   │       │   └── FileController.java
│   │   │       ├── service/
│   │   │       │   ├── BoardService.java
│   │   │       │   └── FileStorageService.java
│   │   │       ├── repository/
│   │   │       │   ├── BoardRepository.java
│   │   │       │   └── AttachmentRepository.java
│   │   │       ├── entity/
│   │   │       │   ├── Board.java
│   │   │       │   └── Attachment.java
│   │   │       ├── dto/
│   │   │       │   └── BoardForm.java
│   │   │       └── exception/
│   │   │           └── FileStorageException.java
│   │   └── resources/
│   │       ├── templates/
│   │       │   ├── board/
│   │       │   │   ├── list.html
│   │       │   │   ├── write.html
│   │       │   │   └── view.html
│   │       └── application.yml
│   └── test/
│       └── java/
│           └── com/example/board/
│               └── FileUploadTest.java
└── pom.xml
```

### 단계별 구현 가이드

#### 1단계: 프로젝트 초기 설정

**pom.xml**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <dependencies>
        <!-- Spring Boot Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Spring Boot JPA -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- MySQL -->
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
        </dependency>

        <!-- Thymeleaf -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-thymeleaf</artifactId>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
        </dependency>
    </dependencies>
</project>
```

**application.yml**:
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/board_db
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true

  servlet:
    multipart:
      enabled: true
      max-file-size: 10MB
      max-request-size: 50MB
      file-size-threshold: 1MB
      location: /tmp

file:
  upload-dir: uploads
```

**체크포인트**:
- [ ] 프로젝트 생성 완료
- [ ] 의존성 추가 완료
- [ ] application.yml 설정 완료

---

#### 2단계: Entity 작성

**Board.java**:
```java
package com.example.board.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "boards")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Board {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;

    @Column(nullable = false, length = 50)
    private String author;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @Column(nullable = false)
    private int viewCount;

    // 양방향 관계 (게시글 삭제 시 첨부파일도 삭제)
    @OneToMany(mappedBy = "board", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Attachment> attachments = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        viewCount = 0;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // 연관관계 편의 메서드
    public void addAttachment(Attachment attachment) {
        attachments.add(attachment);
        attachment.setBoard(this);
    }

    public void removeAttachment(Attachment attachment) {
        attachments.remove(attachment);
        attachment.setBoard(null);
    }
}
```

**Attachment.java**:
```java
package com.example.board.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "attachments")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Attachment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "board_id", nullable = false)
    private Board board;

    @Column(nullable = false, length = 255)
    private String originalFilename;  // 원본 파일명

    @Column(nullable = false, length = 255)
    private String storedFilename;  // 저장된 파일명 (UUID)

    @Column(nullable = false)
    private String filePath;  // 파일 경로

    @Column(nullable = false)
    private Long fileSize;  // 파일 크기 (bytes)

    @Column(nullable = false, length = 100)
    private String contentType;  // MIME 타입

    @Column(nullable = false)
    private LocalDateTime uploadedAt;

    @Column(nullable = false)
    @Builder.Default
    private int downloadCount = 0;  // 다운로드 횟수

    @PrePersist
    protected void onCreate() {
        uploadedAt = LocalDateTime.now();
    }

    public void incrementDownloadCount() {
        this.downloadCount++;
    }
}
```

**Repository**:
```java
package com.example.board.repository;

import com.example.board.entity.Board;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

```java
package com.example.board.repository;

import com.example.board.entity.Attachment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AttachmentRepository extends JpaRepository<Attachment, Long> {
    List<Attachment> findByBoardId(Long boardId);
}
```

---

#### 3단계: Service 작성

**FileStorageService.java**:
```java
package com.example.board.service;

import com.example.board.entity.Attachment;
import com.example.board.entity.Board;
import com.example.board.exception.FileStorageException;
import com.example.board.repository.AttachmentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class FileStorageService {

    private final AttachmentRepository attachmentRepository;

    @Value("${file.upload-dir}")
    private String uploadDir;

    private static final List<String> ALLOWED_EXTENSIONS = Arrays.asList(
        "jpg", "jpeg", "png", "gif",  // 이미지
        "pdf", "doc", "docx", "xls", "xlsx",  // 문서
        "zip", "rar"  // 압축
    );

    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024;  // 10MB

    /**
     * 파일 저장
     */
    @Transactional
    public List<Attachment> storeFiles(Board board, List<MultipartFile> files) {
        if (files == null || files.isEmpty()) {
            return new ArrayList<>();
        }

        // 파일 개수 검증 (최대 5개)
        if (files.size() > 5) {
            throw new FileStorageException("파일은 최대 5개까지 업로드 가능합니다");
        }

        // 전체 파일 크기 검증 (최대 50MB)
        long totalSize = files.stream()
            .mapToLong(MultipartFile::getSize)
            .sum();

        if (totalSize > 50 * 1024 * 1024) {
            throw new FileStorageException("전체 파일 크기는 50MB를 초과할 수 없습니다");
        }

        List<Attachment> attachments = new ArrayList<>();

        for (MultipartFile file : files) {
            if (!file.isEmpty()) {
                Attachment attachment = storeFile(board, file);
                attachments.add(attachment);
            }
        }

        return attachments;
    }

    /**
     * 단일 파일 저장
     */
    private Attachment storeFile(Board board, MultipartFile file) {
        try {
            // 1. 파일 검증
            validateFile(file);

            // 2. 파일명 생성
            String originalFilename = StringUtils.cleanPath(file.getOriginalFilename());
            String extension = getExtension(originalFilename);
            String storedFilename = UUID.randomUUID().toString() + "." + extension;

            // 3. 저장 경로 생성
            Path uploadPath = Paths.get(uploadDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            // 4. 파일 저장
            Path filePath = uploadPath.resolve(storedFilename);
            file.transferTo(filePath);

            // 5. Attachment 엔티티 생성
            Attachment attachment = Attachment.builder()
                .board(board)
                .originalFilename(originalFilename)
                .storedFilename(storedFilename)
                .filePath(filePath.toString())
                .fileSize(file.getSize())
                .contentType(file.getContentType())
                .build();

            return attachmentRepository.save(attachment);

        } catch (IOException e) {
            throw new FileStorageException("파일 저장 실패: " + file.getOriginalFilename(), e);
        }
    }

    /**
     * 파일 삭제
     */
    @Transactional
    public void deleteFile(Long attachmentId) {
        Attachment attachment = attachmentRepository.findById(attachmentId)
            .orElseThrow(() -> new FileStorageException("첨부파일을 찾을 수 없습니다"));

        try {
            // 1. 실제 파일 삭제
            Files.deleteIfExists(Paths.get(attachment.getFilePath()));

            // 2. DB 레코드 삭제
            attachmentRepository.delete(attachment);

        } catch (IOException e) {
            throw new FileStorageException("파일 삭제 실패", e);
        }
    }

    /**
     * 파일 검증
     */
    private void validateFile(MultipartFile file) {
        // 1. 빈 파일 체크
        if (file.isEmpty()) {
            throw new FileStorageException("빈 파일은 업로드할 수 없습니다");
        }

        // 2. 파일 크기 체크
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new FileStorageException(
                String.format("파일 크기가 %.2fMB를 초과합니다 (최대: 10MB)",
                    file.getSize() / (1024.0 * 1024.0))
            );
        }

        // 3. 파일명 체크
        String filename = file.getOriginalFilename();
        if (filename == null || filename.isEmpty()) {
            throw new FileStorageException("파일명이 없습니다");
        }

        // 4. 확장자 체크
        String extension = getExtension(filename);
        if (!ALLOWED_EXTENSIONS.contains(extension.toLowerCase())) {
            throw new FileStorageException(
                "허용되지 않는 파일 형식입니다. 허용: " + ALLOWED_EXTENSIONS
            );
        }

        // 5. 경로 조작 방지
        if (filename.contains("..")) {
            throw new FileStorageException("파일명에 부적절한 경로가 포함되어 있습니다");
        }
    }

    /**
     * 확장자 추출
     */
    private String getExtension(String filename) {
        int lastDot = filename.lastIndexOf('.');
        if (lastDot == -1) {
            throw new FileStorageException("파일 확장자가 없습니다");
        }
        return filename.substring(lastDot + 1);
    }

    /**
     * 다운로드 횟수 증가
     */
    @Transactional
    public void incrementDownloadCount(Long attachmentId) {
        Attachment attachment = attachmentRepository.findById(attachmentId)
            .orElseThrow(() -> new FileStorageException("첨부파일을 찾을 수 없습니다"));

        attachment.incrementDownloadCount();
    }
}
```

**BoardService.java**:
```java
package com.example.board.service;

import com.example.board.dto.BoardForm;
import com.example.board.entity.Attachment;
import com.example.board.entity.Board;
import com.example.board.repository.BoardRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BoardService {

    private final BoardRepository boardRepository;
    private final FileStorageService fileStorageService;

    /**
     * 게시글 저장 (파일 포함)
     */
    @Transactional
    public Board save(BoardForm boardForm, List<MultipartFile> files) {
        // 1. 게시글 저장
        Board board = Board.builder()
            .title(boardForm.getTitle())
            .content(boardForm.getContent())
            .author(boardForm.getAuthor())
            .build();

        Board savedBoard = boardRepository.save(board);

        // 2. 파일 저장
        if (files != null && !files.isEmpty()) {
            List<Attachment> attachments = fileStorageService.storeFiles(savedBoard, files);
            attachments.forEach(savedBoard::addAttachment);
        }

        return savedBoard;
    }

    /**
     * 게시글 조회 (조회수 증가)
     */
    @Transactional
    public Board findById(Long id) {
        Board board = boardRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다"));

        board.setViewCount(board.getViewCount() + 1);

        return board;
    }

    /**
     * 전체 게시글 조회
     */
    public List<Board> findAll() {
        return boardRepository.findAll();
    }

    /**
     * 게시글 삭제 (파일도 함께 삭제)
     */
    @Transactional
    public void delete(Long id) {
        Board board = boardRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다"));

        // 첨부파일 삭제 (cascade로 자동 삭제되지만 실제 파일 삭제 필요)
        board.getAttachments().forEach(attachment ->
            fileStorageService.deleteFile(attachment.getId())
        );

        boardRepository.delete(board);
    }
}
```

---

#### 4단계: Controller 작성

**BoardController.java**:
```java
package com.example.board.controller;

import com.example.board.dto.BoardForm;
import com.example.board.entity.Board;
import com.example.board.service.BoardService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.List;

@Controller
@RequestMapping("/board")
@RequiredArgsConstructor
public class BoardController {

    private final BoardService boardService;

    /**
     * 게시글 목록
     */
    @GetMapping
    public String list(Model model) {
        List<Board> boards = boardService.findAll();
        model.addAttribute("boards", boards);
        return "board/list";
    }

    /**
     * 게시글 작성 폼
     */
    @GetMapping("/write")
    public String writeForm(Model model) {
        model.addAttribute("boardForm", new BoardForm());
        return "board/write";
    }

    /**
     * 게시글 저장
     */
    @PostMapping("/write")
    public String write(
        @ModelAttribute BoardForm boardForm,
        @RequestParam(value = "files", required = false) List<MultipartFile> files,
        RedirectAttributes redirectAttributes
    ) {
        try {
            Board board = boardService.save(boardForm, files);

            redirectAttributes.addFlashAttribute("message", "게시글이 등록되었습니다");
            return "redirect:/board/" + board.getId();

        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("error", e.getMessage());
            return "redirect:/board/write";
        }
    }

    /**
     * 게시글 상세
     */
    @GetMapping("/{id}")
    public String view(@PathVariable Long id, Model model) {
        Board board = boardService.findById(id);
        model.addAttribute("board", board);
        return "board/view";
    }

    /**
     * 게시글 삭제
     */
    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id, RedirectAttributes redirectAttributes) {
        try {
            boardService.delete(id);
            redirectAttributes.addFlashAttribute("message", "게시글이 삭제되었습니다");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("error", "삭제 실패: " + e.getMessage());
        }

        return "redirect:/board";
    }
}
```

**FileController.java**:
```java
package com.example.board.controller;

import com.example.board.entity.Attachment;
import com.example.board.repository.AttachmentRepository;
import com.example.board.service.FileStorageService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;

@RestController
@RequestMapping("/files")
@RequiredArgsConstructor
public class FileController {

    private final AttachmentRepository attachmentRepository;
    private final FileStorageService fileStorageService;

    /**
     * 파일 다운로드
     */
    @GetMapping("/{id}/download")
    public ResponseEntity<Resource> download(@PathVariable Long id) throws UnsupportedEncodingException {
        // 1. 첨부파일 조회
        Attachment attachment = attachmentRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("첨부파일을 찾을 수 없습니다"));

        // 2. 파일 읽기
        Path path = Paths.get(attachment.getFilePath());
        Resource resource = new FileSystemResource(path);

        if (!resource.exists()) {
            throw new RuntimeException("파일이 존재하지 않습니다");
        }

        // 3. 다운로드 횟수 증가
        fileStorageService.incrementDownloadCount(id);

        // 4. 한글 파일명 인코딩
        String encodedFilename = URLEncoder.encode(
            attachment.getOriginalFilename(),
            StandardCharsets.UTF_8
        ).replaceAll("\\+", "%20");

        // 5. 응답
        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(attachment.getContentType()))
            .header(HttpHeaders.CONTENT_DISPOSITION,
                "attachment; filename*=UTF-8''" + encodedFilename)
            .body(resource);
    }

    /**
     * 이미지 미리보기
     */
    @GetMapping("/{id}/preview")
    public ResponseEntity<Resource> preview(@PathVariable Long id) {
        Attachment attachment = attachmentRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("첨부파일을 찾을 수 없습니다"));

        Path path = Paths.get(attachment.getFilePath());
        Resource resource = new FileSystemResource(path);

        if (!resource.exists()) {
            throw new RuntimeException("파일이 존재하지 않습니다");
        }

        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(attachment.getContentType()))
            .header(HttpHeaders.CONTENT_DISPOSITION, "inline")
            .body(resource);
    }
}
```

---

#### 5단계: View 작성 (Thymeleaf)

**list.html** (게시글 목록):
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>게시판</title>
</head>
<body>
    <h1>게시판</h1>

    <a href="/board/write">글쓰기</a>

    <table border="1">
        <thead>
            <tr>
                <th>번호</th>
                <th>제목</th>
                <th>작성자</th>
                <th>작성일</th>
                <th>조회수</th>
                <th>첨부</th>
            </tr>
        </thead>
        <tbody>
            <tr th:each="board : ${boards}">
                <td th:text="${board.id}"></td>
                <td>
                    <a th:href="@{/board/{id}(id=${board.id})}"
                       th:text="${board.title}"></a>
                </td>
                <td th:text="${board.author}"></td>
                <td th:text="${#temporals.format(board.createdAt, 'yyyy-MM-dd')}"></td>
                <td th:text="${board.viewCount}"></td>
                <td th:text="${board.attachments.size()}"></td>
            </tr>
        </tbody>
    </table>
</body>
</html>
```

**write.html** (게시글 작성):
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>글쓰기</title>
</head>
<body>
    <h1>글쓰기</h1>

    <form th:action="@{/board/write}"
          method="post"
          enctype="multipart/form-data">

        <div>
            <label>제목:</label>
            <input type="text" name="title" required>
        </div>

        <div>
            <label>작성자:</label>
            <input type="text" name="author" required>
        </div>

        <div>
            <label>내용:</label>
            <textarea name="content" rows="10" cols="50" required></textarea>
        </div>

        <div>
            <label>첨부파일 (최대 5개, 각 10MB):</label>
            <input type="file" name="files" multiple>
            <p style="color: gray; font-size: 12px;">
                허용 형식: 이미지(jpg, png), 문서(pdf, docx), 압축(zip)
            </p>
        </div>

        <button type="submit">등록</button>
        <a href="/board">취소</a>
    </form>
</body>
</html>
```

**view.html** (게시글 상세):
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title th:text="${board.title}">게시글 상세</title>
</head>
<body>
    <h1 th:text="${board.title}"></h1>

    <p>작성자: <span th:text="${board.author}"></span></p>
    <p>작성일: <span th:text="${#temporals.format(board.createdAt, 'yyyy-MM-dd HH:mm')}"></span></p>
    <p>조회수: <span th:text="${board.viewCount}"></span></p>

    <hr>

    <div th:utext="${board.content}"></div>

    <hr>

    <!-- 첨부파일 목록 -->
    <div th:if="${!board.attachments.isEmpty()}">
        <h3>첨부파일 (<span th:text="${board.attachments.size()}"></span>개)</h3>
        <ul>
            <li th:each="attachment : ${board.attachments}">
                <!-- 이미지 미리보기 -->
                <div th:if="${attachment.contentType.startsWith('image/')}">
                    <img th:src="@{/files/{id}/preview(id=${attachment.id})}"
                         style="max-width: 300px;"
                         th:alt="${attachment.originalFilename}">
                </div>

                <!-- 파일 정보 -->
                <a th:href="@{/files/{id}/download(id=${attachment.id})}"
                   th:text="${attachment.originalFilename}"></a>
                (<span th:text="${#numbers.formatDecimal(attachment.fileSize / 1024.0, 1, 'COMMA', 2, 'POINT')}"></span> KB,
                다운로드 <span th:text="${attachment.downloadCount}"></span>회)
            </li>
        </ul>
    </div>

    <hr>

    <a href="/board">목록</a>

    <form th:action="@{/board/{id}/delete(id=${board.id})}"
          method="post"
          style="display: inline;"
          onsubmit="return confirm('정말 삭제하시겠습니까?');">
        <button type="submit">삭제</button>
    </form>
</body>
</html>
```

---

### 실행 결과

1. **게시글 작성**:
   - 제목, 내용, 작성자 입력
   - 파일 최대 5개 첨부
   - 저장 버튼 클릭

2. **게시글 목록**:
   - 모든 게시글 표시
   - 첨부파일 개수 표시

3. **게시글 상세**:
   - 이미지 파일은 미리보기
   - 문서 파일은 다운로드 링크
   - 다운로드 횟수 표시

4. **파일 다운로드**:
   - 파일 클릭 시 다운로드
   - 한글 파일명 정상 표시
   - 다운로드 횟수 자동 증가

---

## 📝 핵심 정리

### 파일 업로드 실무 체크리스트

#### 필수 구현 사항
- [ ] 파일 검증 (크기, 확장자, MIME)
- [ ] 파일명 안전화 (UUID 사용)
- [ ] 트랜잭션 관리
- [ ] 에러 처리
- [ ] 파일-DB 정보 동기화

#### 보안 체크리스트
- [ ] 확장자 화이트리스트
- [ ] 경로 조작 방지 (..)
- [ ] 파일 크기 제한
- [ ] MIME 타입 검증
- [ ] 실제 경로 노출 방지

#### 성능 최적화
- [ ] transferTo() 사용
- [ ] 비동기 처리 (@Async)
- [ ] 청크 업로드 (대용량)
- [ ] CDN 연동 (정적 파일)

---

## ❓ FAQ

<details>
<summary><strong>Q1: S3 업로드 시 파일이 public으로 공개되는데 보안 문제는 없나요?</strong></summary>

**A**: CDN 연동을 위해 public 설정했지만, 실제로는 **서명된 URL (Signed URL)** 을 사용하는 것이 더 안전합니다.

**보안 강화 방법**:

```java
// ✅ Signed URL 생성 (유효기간 1시간)
public String generatePresignedUrl(String key) {
    Date expiration = new Date();
    expiration.setTime(expiration.getTime() + 3600 * 1000);  // 1시간

    GeneratePresignedUrlRequest request = new GeneratePresignedUrlRequest(bucket, key)
        .withMethod(HttpMethod.GET)
        .withExpiration(expiration);

    URL url = amazonS3.generatePresignedUrl(request);
    return url.toString();
}

// 이제 파일을 private으로 설정 가능
PutObjectRequest request = new PutObjectRequest(bucket, key, inputStream, metadata)
    .withCannedAcl(CannedAccessControlList.Private);  // ✅ Private
```

**실무 팁**:
- 💡 민감한 파일(신분증, 계약서)은 반드시 Private + Signed URL
- 💡 공개 이미지(프로필 사진)는 Public + CloudFront 캐싱
- 💡 Signed URL 유효기간은 용도에 따라 조정 (다운로드: 1시간, 스트리밍: 24시간)

</details>

<details>
<summary><strong>Q2: 이미지 리사이징 시 품질이 떨어지는데 어떻게 해야 하나요?</strong></summary>

**A**: 리사이징 알고리즘과 압축 품질을 조정해야 합니다.

**고품질 리사이징**:

```java
// ❌ 낮은 품질
Thumbnails.of(image)
    .size(800, 600)
    .toFile(output);

// ✅ 고품질
Thumbnails.of(image)
    .size(800, 600)
    .outputQuality(0.95)  // 품질 95%
    .imageType(BufferedImage.TYPE_INT_RGB)  // RGB 모드
    .asBufferedImage();
```

**품질 vs 용량 트레이드오프**:

| 품질 | 용량 | 용도 |
|------|------|------|
| 0.95 | 100% | 포트폴리오, 상품 상세 |
| 0.85 | 60% | 일반 게시글 |
| 0.70 | 40% | 썸네일 |
| 0.50 | 20% | 작은 아이콘 |

**실무 팁**:
- 💡 프로필 사진: 0.85 (품질과 용량 균형)
- 💡 상품 사진: 0.90 (높은 품질 필요)
- 💡 썸네일: 0.70 (작은 크기라 품질 덜 중요)

</details>

<details>
<summary><strong>Q3: 청크 업로드 중 네트워크가 끊겼는데 어떻게 재개하나요?</strong></summary>

**A**: **업로드 세션 정보를 저장**하고, 재개 시 이미 업로드된 청크를 건너뛰어야 합니다.

**재개 가능한 업로드 구현**:

```java
// 1. 프론트엔드: 업로드 상태 저장
localStorage.setItem('uploadId_' + file.name, uploadId);
localStorage.setItem('uploadedChunks_' + file.name, JSON.stringify(uploadedChunks));

// 2. 재개 시 상태 복원
const savedUploadId = localStorage.getItem('uploadId_' + file.name);
const savedChunks = JSON.parse(localStorage.getItem('uploadedChunks_' + file.name) || '[]');

// 3. 이미 업로드된 청크는 건너뛰기
for (let i = 0; i < totalChunks; i++) {
    if (savedChunks.includes(i)) {
        continue;  // 건너뛰기
    }

    // 업로드
    await uploadChunk(uploadId, i, chunk);

    // 상태 업데이트
    savedChunks.push(i);
    localStorage.setItem('uploadedChunks_' + file.name, JSON.stringify(savedChunks));
}

// 4. 완료 후 정리
localStorage.removeItem('uploadId_' + file.name);
localStorage.removeItem('uploadedChunks_' + file.name);
```

**실무 팁**:
- 💡 네트워크 오류 감지 후 자동 재시도
- 💡 업로드 상태를 localStorage에 저장
- 💡 완료 후 임시 데이터 삭제

</details>

<details>
<summary><strong>Q4: 파일 업로드 시 @Transactional을 사용해야 하나요?</strong></summary>

**A**: **경우에 따라 다릅니다**. 파일 저장과 DB 저장의 일관성이 중요한지 판단해야 합니다.

**시나리오 1: 트랜잭션 필요**
```java
@Transactional
public void uploadWithTransaction(MultipartFile file) {
    // 1. DB 저장
    FileMetadata metadata = fileRepository.save(new FileMetadata(...));

    try {
        // 2. 파일 저장
        file.transferTo(path);
    } catch (IOException e) {
        // 롤백됨! DB 저장도 취소
        throw new RuntimeException(e);
    }
}
```

**시나리오 2: 트랜잭션 불필요 (파일 먼저 저장)**
```java
public void uploadWithoutTransaction(MultipartFile file) {
    try {
        // 1. 파일 먼저 저장
        file.transferTo(path);

        // 2. 파일 저장 성공 후 DB 저장
        if (Files.exists(path)) {
            fileRepository.save(new FileMetadata(...));
        }
    } catch (IOException e) {
        // 파일 저장 실패 시 DB 저장 안 함
        throw new RuntimeException(e);
    }
}
```

**권장 방식**:
```java
@Service
public class FileUploadService {

    @Transactional
    public FileMetadata upload(MultipartFile file) throws IOException {
        // 1. 파일 먼저 저장 (트랜잭션 외부)
        Path savedPath = saveFileToFileSystem(file);

        try {
            // 2. DB 저장 (트랜잭션 내부)
            FileMetadata metadata = FileMetadata.builder()
                .path(savedPath.toString())
                .build();

            return fileRepository.save(metadata);

        } catch (Exception e) {
            // DB 저장 실패 시 파일 삭제
            Files.deleteIfExists(savedPath);
            throw e;
        }
    }
}
```

**실무 팁**:
- 💡 파일 저장 먼저, DB 저장 나중에
- 💡 DB 저장 실패 시 파일 수동 삭제
- 💡 대용량 파일은 트랜잭션 타임아웃 주의

</details>

<details>
<summary><strong>Q5: 이미지 업로드 시 EXIF 정보(GPS, 카메라)가 노출되는데 안전한가요?</strong></summary>

**A**: **보안을 위해 EXIF 메타데이터를 제거**해야 합니다.

**EXIF 정보 제거**:

```java
import org.apache.commons.imaging.Imaging;
import org.apache.commons.imaging.formats.jpeg.JpegImageMetadata;
import org.apache.commons.imaging.formats.jpeg.exif.ExifRewriter;

public BufferedImage removeExif(MultipartFile file) throws Exception {
    // 1. 이미지 읽기
    BufferedImage image = ImageIO.read(file.getInputStream());

    // 2. EXIF 제거 후 저장
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    ImageIO.write(image, "jpg", baos);

    // 3. 새 이미지 반환 (EXIF 없음)
    return ImageIO.read(new ByteArrayInputStream(baos.toByteArray()));
}

// 또는 Thumbnailator 사용
public BufferedImage removeExifWithThumbnailator(MultipartFile file) throws Exception {
    return Thumbnails.of(file.getInputStream())
        .scale(1.0)  // 크기 유지
        .useExifOrientation(false)  // EXIF 방향 무시
        .asBufferedImage();  // EXIF 제거됨
}
```

**주의해야 할 EXIF 정보**:
- GPS 좌표 (위치 노출)
- 카메라 모델
- 촬영 날짜/시간
- 카메라 설정 (ISO, 조리개)

**실무 팁**:
- 💡 프로필 사진, 신분증은 반드시 EXIF 제거
- 💡 Thumbnailator 리사이징 시 자동으로 EXIF 제거됨
- 💡 원본 보관이 필요하면 별도 저장

</details>

<details>
<summary><strong>Q6: 파일 업로드 속도를 더 빠르게 하려면?</strong></summary>

**A**: 여러 최적화 기법을 조합해야 합니다.

**1. transferTo() 사용**:
```java
// ❌ 느림 (100MB: 10초)
byte[] bytes = file.getBytes();
Files.write(path, bytes);

// ✅ 빠름 (100MB: 1초)
file.transferTo(path);
```

**2. 비동기 처리**:
```java
@Async
public CompletableFuture<String> uploadAsync(MultipartFile file) {
    // 비동기로 처리하여 응답 속도 향상
    file.transferTo(path);
    return CompletableFuture.completedFuture(path.toString());
}
```

**3. 청크 병렬 업로드**:
```javascript
// 여러 청크를 동시에 업로드
const uploadPromises = chunks.map((chunk, index) =>
    fetch('/api/upload/chunk', {
        method: 'POST',
        body: createFormData(chunk, index)
    })
);

await Promise.all(uploadPromises);  // 병렬 실행
```

**4. CDN 직접 업로드**:
```java
// 서버를 거치지 않고 직접 S3/CDN에 업로드
String presignedUrl = generatePresignedUrlForUpload();
return presignedUrl;  // 클라이언트가 직접 업로드
```

**성능 비교**:

| 방법 | 100MB 파일 | 개선율 |
|------|-----------|--------|
| getBytes() + write() | 10초 | - |
| transferTo() | 1초 | 90%↓ |
| transferTo() + 비동기 | 0.5초 | 95%↓ |
| 청크 병렬 업로드 | 0.3초 | 97%↓ |
| CDN 직접 업로드 | 0.1초 | 99%↓ |

</details>

<details>
<summary><strong>Q7: 동영상 업로드 시 썸네일을 자동 생성하려면?</strong></summary>

**A**: **FFmpeg**를 사용하여 동영상에서 프레임을 추출합니다.

**FFmpeg 설치**:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

**Java에서 FFmpeg 사용**:

```java
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class VideoThumbnailGenerator {

    public void generateThumbnail(String videoPath, String thumbnailPath) throws Exception {
        // FFmpeg 명령어
        String[] command = {
            "ffmpeg",
            "-i", videoPath,                    // 입력 동영상
            "-ss", "00:00:01.000",              // 1초 지점
            "-vframes", "1",                    // 1프레임만
            "-vf", "scale=320:240",             // 크기 조정
            thumbnailPath                       // 출력 경로
        };

        // 프로세스 실행
        Process process = Runtime.getRuntime().exec(command);

        // 출력 읽기
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(process.getErrorStream())
        );

        String line;
        while ((line = reader.readLine()) != null) {
            System.out.println(line);
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("썸네일 생성 실패");
        }
    }
}
```

**또는 JAVE2 라이브러리 사용**:

```xml
<dependency>
    <groupId>ws.schild</groupId>
    <artifactId>jave-core</artifactId>
    <version>3.3.1</version>
</dependency>
```

```java
import ws.schild.jave.*;

public void generateThumbnailWithJave(File videoFile, File thumbnailFile) throws Exception {
    MultimediaObject source = new MultimediaObject(videoFile);

    // 썸네일 추출 (1초 지점)
    Encoder encoder = new Encoder();
    EncodingAttributes attrs = new EncodingAttributes();
    attrs.setOffset(1.0f);  // 1초
    attrs.setDuration(0.001f);  // 1프레임

    VideoAttributes video = new VideoAttributes();
    video.setSize(new VideoSize(320, 240));
    attrs.setVideoAttributes(video);

    encoder.encode(source, thumbnailFile, attrs);
}
```

**실무 팁**:
- 💡 썸네일은 비동기로 생성 (@Async)
- 💡 여러 지점(0초, 중간, 마지막)의 썸네일 생성
- 💡 썸네일 생성 실패 시 기본 이미지 사용

</details>

---

## 💼 면접 질문 리스트

### 📘 주니어/신입 개발자용

<details>
<summary><strong>1. S3 파일 업로드와 로컬 파일 시스템 업로드의 차이는 무엇인가요?</strong></summary>

**모범 답안 포인트**:
- 로컬: 서버 디스크에 저장, 서버 재시작 시 유지, 용량 제한 있음
- S3: 클라우드 스토리지, 무한 확장 가능, CDN 연동 가능
- 로컬은 간단하지만 확장성 제한, S3는 비용 발생하지만 확장성 우수

**예시 답변**:
> "로컬 파일 시스템 업로드는 서버의 디스크에 직접 파일을 저장하는 방식이고, S3는 AWS 클라우드 스토리지에 저장하는 방식입니다. 로컬 방식은 구현이 간단하고 추가 비용이 없지만, 서버 디스크 용량 제한이 있고 서버가 여러 대일 경우 파일 동기화 문제가 발생합니다. 반면 S3는 무한 확장이 가능하고 CDN 연동으로 빠른 이미지 제공이 가능하지만, API 호출 비용과 스토리지 비용이 발생합니다."

**꼬리 질문**:
- Q: S3 말고 다른 클라우드 스토리지는 어떤 게 있나요?
- A: Google Cloud Storage, Azure Blob Storage, Naver Object Storage 등이 있습니다.

**실무 연관**:
- 소규모 프로젝트: 로컬 파일 시스템
- 대규모/확장 가능한 서비스: S3

</details>

<details>
<summary><strong>2. 이미지 리사이징은 언제 하는 게 좋나요?</strong></summary>

**모범 답안 포인트**:
- 업로드 시점에 리사이징 (서버 부담, 사용자 대기 시간)
- 비동기로 리사이징 (사용자 경험 향상)
- 여러 크기 미리 생성 (썸네일, 중간, 원본)

**예시 답변**:
> "이미지 리사이징은 업로드 직후 비동기로 처리하는 것이 좋습니다. 사용자가 업로드 버튼을 누르면 원본을 먼저 저장하고, 백그라운드에서 리사이징을 진행합니다. 이렇게 하면 사용자는 업로드 완료를 빠르게 확인할 수 있고, 리사이징은 서버에서 천천히 처리됩니다. 또한 프로필 사진처럼 여러 크기가 필요한 경우 50x50, 150x150, 300x300 등 미리 생성해두면 나중에 빠르게 제공할 수 있습니다."

**꼬리 질문**:
- Q: 리사이징 중 에러가 발생하면 어떻게 처리하나요?
- A: 원본은 유지하고, 리사이징 실패 시 기본 썸네일 이미지를 사용하거나 재시도 큐에 넣습니다.

</details>

<details>
<summary><strong>3. 파일 업로드 시 보안 문제는 어떤 게 있나요?</strong></summary>

**모범 답안 포인트**:
- 악성 파일 업로드 (exe, sh)
- 경로 조작 공격 (../)
- 파일 크기 제한 없음 (DoS)
- EXIF 정보 노출 (GPS)

**예시 답변**:
> "파일 업로드 시 주요 보안 문제는 네 가지입니다. 첫째, 악성 실행 파일(.exe, .sh)을 업로드하여 서버를 공격할 수 있습니다. 둘째, '../../../etc/passwd' 같은 경로로 시스템 파일을 덮어쓸 수 있습니다. 셋째, 파일 크기 제한이 없으면 대용량 파일로 서버 디스크를 가득 채울 수 있습니다. 넷째, 이미지의 EXIF 정보에 GPS 좌표가 포함되어 촬영 위치가 노출될 수 있습니다. 따라서 확장자 화이트리스트, 경로 검증, 크기 제한, EXIF 제거를 반드시 해야 합니다."

**꼬리 질문**:
- Q: 확장자만 검증하면 안전한가요?
- A: 아닙니다. 파일 확장자는 쉽게 변경할 수 있으므로 MIME 타입과 매직 넘버까지 검증해야 합니다.

</details>

<details>
<summary><strong>4. transferTo()를 사용하는 이유는 무엇인가요?</strong></summary>

**모범 답안 포인트**:
- 스트리밍 방식으로 메모리 효율적
- 버퍼 사용으로 I/O 횟수 감소
- getBytes()보다 100배 빠름

**예시 답변**:
> "transferTo()는 파일을 스트리밍 방식으로 저장하기 때문에 메모리 효율적입니다. getBytes()를 사용하면 파일 전체를 메모리에 올려야 하므로 100MB 파일은 100MB 메모리를 사용하지만, transferTo()는 버퍼 크기(보통 8KB)만 사용합니다. 또한 버퍼를 사용하여 디스크 I/O 횟수를 줄이므로 속도도 훨씬 빠릅니다. 실제로 100MB 파일 업로드 시 getBytes()는 10초, transferTo()는 1초 정도 걸립니다."

**꼬리 질문**:
- Q: 버퍼 크기를 조정할 수 있나요?
- A: application.yml에서 `file-size-threshold` 설정으로 조정 가능합니다.

</details>

<details>
<summary><strong>5. 청크 업로드는 언제 사용하나요?</strong></summary>

**모범 답안 포인트**:
- 대용량 파일 (100MB 이상)
- 네트워크 불안정한 환경
- 업로드 재개 필요할 때

**예시 답변**:
> "청크 업로드는 대용량 파일을 작은 조각(청크)으로 나누어 업로드하는 방식입니다. 100MB 이상 대용량 파일이나 모바일처럼 네트워크가 불안정한 환경에서 사용합니다. 예를 들어 1GB 파일을 5MB씩 200개 청크로 나누면, 중간에 네트워크가 끊겨도 이미 업로드된 청크는 유지되어 재개할 수 있습니다. 구글 드라이브, 유튜브 같은 서비스가 이 방식을 사용합니다."

**꼬리 질문**:
- Q: 청크 크기는 어떻게 결정하나요?
- A: 보통 5MB~10MB가 적당합니다. 너무 작으면 요청 횟수가 많아지고, 너무 크면 재업로드 부담이 커집니다.

</details>

---

### 📗 중급 개발자용

<details>
<summary><strong>1. S3 Multipart Upload의 동작 원리는 무엇인가요?</strong></summary>

**모범 답안 포인트**:
- Initiate: 업로드 ID 발급
- Upload Parts: 파트 번호와 ETag 반환
- Complete: 파트 병합

**예시 답변** (중급):
> "S3 Multipart Upload는 세 단계로 동작합니다. 첫째, Initiate Multipart Upload로 업로드 ID를 발급받습니다. 둘째, 각 파트를 Upload Part로 업로드하면 ETag가 반환됩니다. 셋째, Complete Multipart Upload로 모든 파트의 ETag를 전송하면 S3가 파트들을 병합합니다. 이 방식의 장점은 파트를 병렬로 업로드할 수 있고, 실패한 파트만 재업로드하면 되며, 최대 5TB까지 업로드 가능하다는 점입니다. 실제 프로젝트에서 1GB 영상 파일을 50개 파트로 나누어 병렬 업로드하여 기존 10분에서 2분으로 단축한 경험이 있습니다."

**심화 꼬리 질문**:
- Q: Abort Multipart Upload는 언제 사용하나요?
- A: 업로드 중단 시 사용합니다. 그렇지 않으면 미완성 파트들이 S3에 남아 스토리지 비용이 발생합니다.

**실무 예시**:
```java
// 1. Initiate
String uploadId = s3.initiateMultipartUpload(request).getUploadId();

// 2. Upload Parts (병렬)
List<CompletableFuture<PartETag>> futures = parts.stream()
    .map(part -> CompletableFuture.supplyAsync(() ->
        s3.uploadPart(createUploadPartRequest(uploadId, part))
    ))
    .collect(Collectors.toList());

List<PartETag> partETags = futures.stream()
    .map(CompletableFuture::join)
    .collect(Collectors.toList());

// 3. Complete
s3.completeMultipartUpload(new CompleteMultipartUploadRequest()
    .withUploadId(uploadId)
    .withPartETags(partETags));
```

</details>

<details>
<summary><strong>2. 파일 업로드 시 트랜잭션 처리 전략은 무엇인가요?</strong></summary>

**모범 답안 포인트**:
- 파일 저장은 트랜잭션 외부
- DB 저장은 트랜잭션 내부
- Saga 패턴 고려

**예시 답변** (중급):
> "파일 업로드는 파일 저장과 DB 저장의 일관성을 보장해야 하지만, 파일 저장은 트랜잭션 롤백이 불가능합니다. 따라서 두 가지 전략을 사용합니다. 첫째, 파일을 먼저 저장하고 성공 시 DB에 저장합니다. DB 저장 실패 시 파일을 수동으로 삭제합니다. 둘째, Saga 패턴으로 보상 트랜잭션을 구현합니다. 예를 들어 파일 저장 실패 시 이전 단계를 롤백하는 보상 로직을 작성합니다. 실제 프로젝트에서는 이벤트 소싱을 활용하여 파일 업로드 이벤트를 기록하고, 실패 시 재시도 큐에 넣어 처리했습니다."

**트레이드오프**:
- ✅ 파일 먼저: 구현 간단, DB 실패 시 파일 고아
- ✅ DB 먼저: 파일 실패 시 DB 롤백, 파일 고아 없음
- ✅ Saga 패턴: 완벽한 일관성, 구현 복잡

</details>

<details>
<summary><strong>3. CDN을 통한 이미지 제공 시 캐시 무효화는 어떻게 하나요?</strong></summary>

**모범 답안 포인트**:
- CloudFront Invalidation API
- 파일명에 버전/해시 추가
- Cache-Control 헤더

**예시 답변** (중급):
> "CDN 캐시 무효화는 세 가지 방법이 있습니다. 첫째, CloudFront Invalidation API로 특정 파일의 캐시를 즉시 삭제합니다. 하지만 요청 1000개당 $0.005 비용이 발생합니다. 둘째, 파일명에 버전이나 해시를 추가합니다. 예를 들어 profile_v2.jpg나 profile_a3f4d.jpg처럼 변경하면 새 파일로 인식되어 자동으로 캐시 갱신됩니다. 셋째, Cache-Control 헤더로 캐시 유효기간을 설정합니다. 실제 프로젝트에서는 프로필 사진 변경 시 타임스탬프를 URL에 추가하여 캐시 무효화 비용을 0으로 만들었습니다."

**실제 구현**:
```java
// 방법 1: Invalidation API
public void invalidateCache(String path) {
    InvalidationBatch batch = new InvalidationBatch()
        .withPaths(new Paths().withItems("/" + path))
        .withCallerReference(UUID.randomUUID().toString());

    cloudFront.createInvalidation(new CreateInvalidationRequest()
        .withDistributionId(distributionId)
        .withInvalidationBatch(batch));
}

// 방법 2: 파일명에 해시 추가 (권장)
String filename = "profile_" + DigestUtils.md5Hex(file.getBytes()).substring(0, 8) + ".jpg";

// 방법 3: URL에 타임스탬프 추가
String url = cdnDomain + "/profile.jpg?t=" + System.currentTimeMillis();
```

</details>

---

## 💡 면접 질문 답안

### 📘 주니어/신입 개발자용 답안

#### Q1. S3 파일 업로드와 로컬 파일 시스템 업로드의 차이는 무엇인가요?

**완벽한 답변 예시**:
```
"S3와 로컬 파일 시스템의 가장 큰 차이는 확장성과 가용성입니다.

로컬 파일 시스템은 서버의 하드디스크에 직접 저장하는 방식으로, 구현이 간단하고 별도 비용이 들지 않습니다. 하지만 서버 디스크 용량이 한정되어 있고, 서버가 여러 대인 경우 파일 동기화 문제가 발생합니다.

반면 S3는 AWS 클라우드 스토리지로, 사실상 무제한 저장 공간을 제공하고 99.999999999%의 내구성을 보장합니다. 또한 CloudFront CDN과 연동하여 전 세계 사용자에게 빠르게 이미지를 제공할 수 있습니다. 단점은 API 호출 비용과 스토리지 비용이 발생한다는 점입니다.

실무에서는 소규모 프로젝트나 내부 시스템은 로컬 파일 시스템을 사용하고, 사용자가 많은 서비스나 확장 가능한 시스템은 S3를 사용합니다."
```

**답변 구조 분석**:
1. **도입부 (10초)**: 핵심 차이점을 한 문장으로
2. **본론 (30초)**: 각각의 장단점 설명
3. **마무리 (10초)**: 실무 활용 기준

**더 좋은 답변을 위한 추가 포인트**:
- ✅ 구체적 수치 언급 (99.999999999% 내구성)
- ✅ 실무 사용 기준 제시
- ✅ 비용 고려사항 언급

**피해야 할 답변 실수**:
- ❌ "S3가 무조건 좋다"는 단정적 표현
- ❌ 비용 언급 없이 S3만 추천
- ❌ 실무 경험 없이 이론만 나열

**꼬리 질문 대응**:
- Q: "S3 비용은 얼마나 나오나요?"
  - A: "스토리지는 GB당 $0.023, API 요청은 1000건당 $0.0004입니다. 월 10GB 저장 + 100만 요청 시 약 $0.6 정도입니다."

---

#### Q2. 이미지 리사이징은 언제 하는 게 좋나요?

**완벽한 답변 예시**:
```
"이미지 리사이징은 업로드 직후 비동기로 처리하는 것이 가장 효율적입니다.

사용자가 이미지를 업로드하면 먼저 원본을 S3에 저장하고, 업로드 성공 응답을 즉시 반환합니다. 그 후 백그라운드 작업으로 썸네일을 생성합니다. 이렇게 하면 사용자는 업로드 완료를 빠르게 확인할 수 있고, 리사이징은 서버에서 천천히 처리할 수 있습니다.

프로필 사진처럼 여러 크기가 필요한 경우, 50x50 (목록용), 150x150 (프로필 카드용), 300x300 (상세 페이지용) 등 미리 생성해두면 나중에 요청 시 바로 제공할 수 있어 성능이 좋습니다.

실무에서는 Spring의 @Async를 사용하여 비동기로 처리하고, 썸네일 생성 실패 시 기본 이미지를 사용하도록 구현합니다."
```

**답변 구조 분석**:
1. **도입부 (10초)**: 비동기 처리가 최선
2. **본론 (30초)**: 구현 방법과 이유
3. **마무리 (10초)**: 실무 적용 예시

---

#### Q3. 파일 업로드 시 보안 문제는 어떤 게 있나요?

**완벽한 답변 예시**:
```
"파일 업로드 시 주요 보안 위협은 네 가지입니다.

첫째, 악성 실행 파일 업로드입니다. .exe, .sh 같은 파일을 업로드하여 서버를 공격할 수 있습니다. 이를 방지하려면 허용 확장자 화이트리스트를 만들어야 합니다.

둘째, 경로 조작 공격입니다. '../../../etc/passwd' 같은 파일명으로 시스템 파일을 덮어쓸 수 있습니다. UUID로 파일명을 생성하고 원본 파일명은 DB에만 저장하면 방지할 수 있습니다.

셋째, 서비스 거부 공격입니다. 대용량 파일을 무제한 업로드하여 디스크를 가득 채울 수 있습니다. 파일 크기 제한과 사용자별 할당량을 설정해야 합니다.

넷째, EXIF 정보 노출입니다. 이미지의 EXIF에 GPS 좌표가 포함되어 촬영 위치가 노출될 수 있습니다. 리사이징 시 EXIF를 자동으로 제거하면 해결됩니다."
```

---

#### Q4. transferTo()를 사용하는 이유는 무엇인가요?

**완벽한 답변 예시**:
```
"transferTo()는 파일을 스트리밍 방식으로 저장하여 메모리 효율적이고 빠릅니다.

getBytes()를 사용하면 파일 전체를 메모리에 올려야 합니다. 100MB 파일이면 100MB 메모리를 사용하고, 여러 사용자가 동시에 업로드하면 메모리 부족으로 서버가 다운될 수 있습니다.

반면 transferTo()는 내부적으로 버퍼(보통 8KB)를 사용하여 조금씩 읽고 쓰기를 반복합니다. 따라서 파일 크기와 관계없이 항상 8KB 메모리만 사용합니다. 또한 버퍼를 사용하여 디스크 I/O 횟수를 줄이므로 속도도 훨씬 빠릅니다.

실제 성능 테스트 결과, 100MB 파일 업로드 시 getBytes()는 10초, transferTo()는 1초 정도 걸렸습니다."
```

---

#### Q5. 청크 업로드는 언제 사용하나요?

**완벽한 답변 예시**:
```
"청크 업로드는 대용량 파일을 작은 조각으로 나누어 업로드하는 방식으로, 세 가지 상황에서 유용합니다.

첫째, 100MB 이상 대용량 파일입니다. 1GB 파일을 한 번에 업로드하면 네트워크 오류 시 처음부터 다시 업로드해야 하지만, 5MB씩 200개 청크로 나누면 실패한 청크만 재업로드하면 됩니다.

둘째, 네트워크가 불안정한 환경입니다. 모바일이나 와이파이 환경에서는 연결이 자주 끊기는데, 청크 업로드는 끊긴 지점부터 재개할 수 있습니다.

셋째, 업로드 일시정지/재개 기능이 필요할 때입니다. 구글 드라이브처럼 사용자가 업로드를 일시정지했다가 나중에 재개할 수 있습니다.

실무에서는 동영상, 대용량 압축 파일 같은 경우 청크 업로드를 사용합니다."
```

---

### 📗 중급 개발자용 답안

#### Q1. S3 Multipart Upload의 동작 원리는 무엇인가요?

**완벽한 답변 예시** (중급 수준):
```
"S3 Multipart Upload는 대용량 파일을 여러 파트로 나누어 병렬 업로드하는 방식으로, 세 단계로 동작합니다.

첫 번째 단계는 Initiate Multipart Upload입니다. S3에 업로드를 시작한다고 알리면 고유한 Upload ID가 발급됩니다. 이 ID로 이후 모든 파트를 식별합니다.

두 번째 단계는 Upload Part입니다. 파일을 5MB~5GB 크기의 파트로 나누어 업로드합니다. 각 파트는 1부터 10000까지 번호를 가지며, 업로드 성공 시 ETag가 반환됩니다. 이 단계에서 파트들을 병렬로 업로드하여 속도를 크게 향상시킬 수 있습니다.

세 번째 단계는 Complete Multipart Upload입니다. 모든 파트의 번호와 ETag 목록을 S3에 전송하면, S3가 내부적으로 파트들을 하나의 파일로 병합합니다.

실제 프로젝트에서 1GB 영상 파일을 50개 파트로 나누어 병렬 업로드한 결과, 순차 업로드 10분에서 병렬 업로드 2분으로 단축되었습니다. 또한 네트워크 오류 시 전체를 재업로드하지 않고 실패한 파트만 재업로드하여 성공률을 99%에서 99.9%로 향상시켰습니다."
```

**답변 구조 분석** (중급):
1. **도입부 (15초)**: 개념 + 세 단계 간략히
2. **본론 (60초)**: 각 단계 상세 설명 + 병렬 처리 장점
3. **마무리 (15초)**: 실제 프로젝트 경험 + 성과 수치

**중급 답변의 차별점**:
- ✅ 내부 동작 원리 설명 (Upload ID, ETag)
- ✅ 성능 최적화 방법 (병렬 업로드)
- ✅ 실제 프로젝트 경험 언급
- ✅ 구체적 성과 수치 (10분 → 2분)

---

#### Q2. 파일 업로드 시 트랜잭션 처리 전략은 무엇인가요?

**완벽한 답변 예시** (중급 수준):
```
"파일 업로드는 파일 시스템과 DB라는 두 개의 서로 다른 저장소를 사용하므로, 일반적인 트랜잭션만으로는 일관성을 보장할 수 없습니다. 따라서 보상 트랜잭션 패턴을 사용해야 합니다.

첫 번째 전략은 파일을 먼저 저장하는 방법입니다. 파일 저장이 성공하면 트랜잭션 내에서 DB에 메타데이터를 저장합니다. DB 저장 실패 시 try-catch로 파일을 수동 삭제합니다. 이 방법은 구현이 간단하지만, 예외 발생 시 파일이 고아가 될 수 있습니다.

두 번째 전략은 Saga 패턴입니다. 각 단계마다 보상 로직을 정의하여, 실패 시 이전 단계를 롤백합니다. 예를 들어 파일 저장 → DB 저장 → 썸네일 생성 순서로 진행하다 썸네일 생성 실패 시, DB 삭제 → 파일 삭제 순으로 보상합니다.

세 번째 전략은 이벤트 소싱입니다. 파일 업로드를 이벤트로 기록하고, 비동기로 처리합니다. 실패 시 재시도 큐에 넣어 자동으로 재처리합니다.

실제 프로젝트에서는 첫 번째 방법을 기본으로 사용하고, 중요한 파일(계약서, 신분증)은 Saga 패턴으로 처리했습니다. 그 결과 파일-DB 불일치 문제를 99% 해결했습니다."
```

---

#### Q3. CDN을 통한 이미지 제공 시 캐시 무효화는 어떻게 하나요?

**완벽한 답변 예시** (중급 수준):
```
"CDN 캐시 무효화는 비용과 성능을 모두 고려해야 하므로, 상황에 따라 세 가지 전략을 사용합니다.

첫 번째는 CloudFront Invalidation API를 사용하는 방법입니다. API 호출로 특정 파일의 캐시를 즉시 삭제할 수 있지만, 요청 1000개당 $0.005 비용이 발생합니다. 긴급하게 캐시를 무효화해야 할 때만 사용합니다.

두 번째는 파일명에 버전이나 해시를 추가하는 방법입니다. 예를 들어 profile.jpg를 profile_v2.jpg나 profile_a3f4d.jpg로 변경하면 CDN이 새 파일로 인식하여 자동으로 캐시를 갱신합니다. 비용이 전혀 들지 않으므로 가장 권장되는 방법입니다.

세 번째는 Cache-Control 헤더로 캐시 유효기간을 설정하는 방법입니다. 자주 변경되는 파일은 max-age=3600 (1시간), 거의 변경되지 않는 파일은 max-age=31536000 (1년)으로 설정합니다.

실제 프로젝트에서 프로필 사진 변경 시 타임스탬프를 URL에 추가(profile.jpg?t=1234567890)하여 캐시 무효화 비용을 월 $50에서 $0로 줄였습니다. 정적 파일은 파일명에 해시를 추가하여 캐시 히트율을 95%까지 높였습니다."
```

---

## 📝 핵심 정리 (계속)

**이전 장으로 돌아가기**: [← 이전: 15장 Part 1 - 파일 업로드 기본편](SpringMVC-Part7-15-1-File-Upload-Basic.md)

**다음 장으로 이동**: [다음: 16장 - 예외 처리 →](SpringMVC-Part8-16-Exception-Handling.md)

**목차로 돌아가기**: [📚 전체 목차](README.md)
