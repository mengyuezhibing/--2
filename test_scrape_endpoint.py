import requests
import sys

# 测试登录和 /scrape 端点
def test_scrape_endpoint():
    base_url = 'http://127.0.0.1:8081'
    
    # 创建会话对象，用于保存 cookies
    session = requests.Session()
    
    try:
        # 测试 1: 检查服务器是否响应
        print("测试 1: 检查服务器是否响应...")
        response = session.get(f"{base_url}/login")
        print(f"登录页面状态码: {response.status_code}")
        if response.status_code != 200:
            print("服务器未响应，请检查应用程序是否正在运行。")
            return False
        
        # 测试 2: 登录
        print("\n测试 2: 登录...")
        login_data = {
            'username': 'admin',
            'password': 'admin888'
        }
        response = session.post(f"{base_url}/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        print(f"登录响应: {response.url}")
        
        if response.status_code != 200 and response.status_code != 302:
            print("登录失败")
            return False
        
        # 测试 3: 访问 /scrape 端点（POST 请求）
        print("\n测试 3: 访问 /scrape 端点...")
        scrape_data = {
            'keyword': '人工智能'
        }
        response = session.post(f"{base_url}/scrape", data=scrape_data)
        print(f"/scrape 状态码: {response.status_code}")
        print(f"/scrape 响应: {response.url}")
        
        if response.status_code == 200 or response.status_code == 302:
            print("\n✅ /scrape 端点测试成功！")
            return True
        else:
            print(f"\n❌ /scrape 端点测试失败: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scrape_endpoint()
    sys.exit(0 if success else 1)