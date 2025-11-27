import io
from typing import List, Union, Any

# 필요한 라이브러리가 설치되지 않았을 경우를 대비한 예외 처리
try:
    from PIL import Image
    from sentence_transformers import SentenceTransformer
except ImportError:
    Image = None
    SentenceTransformer = None

class ImageEmbedder:
    def __init__(self, model_name: str = 'clip-ViT-B-32'):
        """
        이미지 임베딩 모델을 초기화합니다.
        기본 모델: clip-ViT-B-32 (가볍고 성능이 준수함)
        """
        if SentenceTransformer is None or Image is None:
            raise ImportError(
                "필수 라이브러리가 설치되지 않았습니다. "
                "다음 명령어로 설치해주세요: pip install sentence-transformers Pillow"
            )
        
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded.")

    def embed(self, image_input: Union[str, bytes, Any]) -> List[float]:
        """
        이미지를 벡터로 변환합니다.
        
        Args:
            image_input: 파일 경로(str), 이미지 바이트(bytes), 또는 PIL Image 객체
            
        Returns:
            임베딩 벡터 (List[float])
        """
        img = self._load_image(image_input)
        
        # 임베딩 생성 (리스트 형태로 반환)
        embedding = self.model.encode(img)
        return embedding.tolist()

    def _load_image(self, image_input: Union[str, bytes, Any]) -> Any:
        """입력 타입을 PIL Image로 변환"""
        if isinstance(image_input, str):
            # 파일 경로인 경우
            return Image.open(image_input)
        elif isinstance(image_input, bytes):
            # 바이트 데이터인 경우
            return Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            # 이미 PIL Image인 경우
            return image_input
        else:
            raise ValueError(f"지원하지 않는 이미지 형식입니다: {type(image_input)}")

# 사용 예시:
# embedder = ImageEmbedder()
# vector = embedder.embed("image.jpg")

class AnimeVectorStore:
    def __init__(self, persist_path: str = "./chroma_data", collection_name: str = "anime_scenes"):
        """
        ChromaDB를 로컬 라이브러리 모드로 초기화합니다.
        데이터는 persist_path에 자동으로 저장됩니다.
        """
        try:
            import chromadb
        except ImportError:
            raise ImportError("chromadb가 설치되지 않았습니다. 'pip install chromadb'를 실행해주세요.")

        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedder = ImageEmbedder()
        print(f"Vector DB initialized at {persist_path}, Collection: {collection_name}")

    def add_image(self, image_path: str, metadata: dict = None):
        """
        이미지를 임베딩하여 DB에 저장합니다.
        AI가 자동으로 상황을 분석하여 메타데이터에 추가합니다.
        
        Args:
            image_path: 이미지 파일 경로
            metadata: 저장할 메타데이터 (기본값 외에 추가할 정보)
        """
        # 0. AI 분석 도구 가져오기
        from app.ai import anime_recommender
        
        # 1. 이미지 임베딩 생성
        vector = self.embedder.embed(image_path)
        
        # 3. ID 생성 (파일 경로를 기반으로 하거나 UUID 사용)
        import uuid
        doc_id = str(uuid.uuid4())
        
        # 4. 메타데이터 병합
        if metadata is None:
            metadata = {}
            
        # 기본 정보 + AI 분석 정보 병합
        metadata["path"] = image_path
        metadata.update(analysis)  # situation, background, mood, time 등이 추가됨
        
        # 5. DB에 저장
        self.collection.add(
            embeddings=[vector],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"Saved image to DB: {image_path} (ID: {doc_id})")
        return doc_id

    def search_similar(self, query_image_input: Union[str, bytes, Any], k: int = 3):
        """
        입력 이미지와 유사한 이미지를 검색합니다.
        """
        # 1. 쿼리 이미지 임베딩
        query_vector = self.embedder.embed(query_image_input)
        
        # 2. 검색 실행
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k
        )
        
        return results

    def ingest_folder(self, folder_path: str):
        """
        지정된 폴더(하위 폴더 포함)의 모든 이미지를 DB에 등록합니다.
        """
        import os
        
        supported_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
        count = 0
        
        print(f"Scanning images in: {folder_path}")
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in supported_exts:
                    full_path = os.path.join(root, file)
                    try:
                        # 메타데이터에 파일명과 상위 폴더명(카테고리 역할) 저장
                        category = os.path.basename(root)
                        self.add_image(full_path, metadata={"filename": file, "category": category})
                        count += 1
                    except Exception as e:
                        print(f"Failed to process {file}: {e}")
                        
        print(f"Successfully ingested {count} images.")

if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때 동작하는 테스트 코드
    import sys
    
    store = AnimeVectorStore()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "ingest" and len(sys.argv) > 2:
            # 사용법: python app/embedding.py ingest "이미지_폴더_경로"
            target_folder = sys.argv[2]
            store.ingest_folder(target_folder)
            
        elif cmd == "search" and len(sys.argv) > 2:
            # 사용법: python app/embedding.py search "검색할_이미지_경로"
            query_image = sys.argv[2]
            results = store.search_similar(query_image)
            print("\nSearch Results:")
            print(results)
    else:
        print("Usage:")
        print("  python app/embedding.py ingest <folder_path>")
        print("  python app/embedding.py search <image_path>")


